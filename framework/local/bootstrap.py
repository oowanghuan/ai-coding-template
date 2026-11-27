"""Additive, versioned project installation using the V3 receipt ownership protocol."""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

from framework.core.protocol import load_json, validate
from framework.local.storage import (atomic_json, authority_lock, canonical, check_install_journal,
                                     fingerprint, root_path, safe_path)
from framework.local.store import envelope, shape, LIVE, UNKNOWN, now
from framework.local.runner import git
from scripts.install_claude_tools import plan as file_plan, rollback as rollback_files, read_receipts, claimed_paths

ROOT = Path(__file__).resolve().parents[2]
VERSION = '0.2.0-preview'
POINTER = b'# Project bootstrap\n\nRead `.ai-org/install-journal.json` and its `guide` path for the installed guide.\nTask authority: `.ai-org/state.json`. Installation does not grant execution rights.\n'


def inventory(root):
    """Fingerprint user files without following symlinks; Git content is never modified."""
    rows = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in list(dirs):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                rows[relative] = {'symlink': os.readlink(path)}
                dirs.remove(name)
            elif relative == '.git':
                # HEAD/index/config changes count; immutable object database is irrelevant.
                dirs.remove(name)
                for entry in ('HEAD', 'index', 'config', 'packed-refs'):
                    p = safe_path(root, '.git/' + entry)
                    if p.exists(): rows['.git/' + entry] = hashlib.sha256(p.read_bytes()).hexdigest()
            elif relative != '.ai-org':
                rows[relative + '/'] = 'directory'
        for name in files:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if relative == '.ai-org/lock': continue
            if path.is_symlink(): rows[relative] = {'symlink': os.readlink(path)}
            elif path.is_file(): rows[relative] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                                  'mode': path.stat().st_mode & 0o777, 'links': path.stat().st_nlink}
            else: raise ValueError('unsupported target file: ' + relative)
    if (root / '.git').exists():
        rows['git-head'] = git(root, 'rev-parse', '--verify', '--quiet', 'HEAD').decode().strip() if has_head(root) else None
    return rows


def has_head(root):
    try:
        git(root, 'rev-parse', '--verify', 'HEAD')
        return True
    except ValueError:
        return False


def initial_snapshot(project_id, owner, baseline, guide, guide_hash):
    # This fixture is an explicit public protocol template; all demo execution data is removed.
    s = load_json(ROOT / 'templates/project/planned.json')
    s['project'].update(id=project_id, owner_principals=[owner])
    w = s['work_packages'][0]
    w.update(project_id=project_id, merger=owner, baseline_sha=baseline,
             spec_refs=[dict(path=guide, version=VERSION, sha256=guide_hash)])
    errors = validate(s, now())
    if errors: raise ValueError('; '.join(errors))
    return s


def idle(state):
    shape(state)
    if state['snapshot']['project']['state_backend'] != 'local_git':
        raise ValueError('different authority backend')
    if any(a['state'] in LIVE for a in state['snapshot']['assignments']) or any(
            w['state'] in UNKNOWN for w in state['workspaces'].values()):
        raise ValueError('active or unknown execution blocks migration')


def plan(root, mode, project_id=None, owner=None, version=VERSION, guide_bytes=None):
    root = root_path(root)
    if mode not in ('init', 'import', 'upgrade'): raise ValueError('unknown installation mode')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}', version): raise ValueError('unsafe version')
    check_install_journal(root)
    state_path = safe_path(root, '.ai-org/state.json')
    journal_path = safe_path(root, '.ai-org/install-journal.json')
    previous = load_json(journal_path) if journal_path.exists() else None
    if mode == 'init' and any(root.iterdir()): raise ValueError('init requires an empty directory; use import')
    if mode == 'upgrade':
        if not previous or previous['state'] != 'committed' or not state_path.exists():
            raise ValueError('upgrade requires a known installation and local authority')
        idle(load_json(state_path))
    elif state_path.exists() or (previous and previous['state'] != 'rolled_back'):
        raise ValueError('existing authority/installation requires explicit upgrade')
    if not owner or not project_id:
        if mode != 'upgrade': raise ValueError('explicit Owner and project ID required')
    guide = '.ai-org/versions/' + version + '/BOOTSTRAP.md'
    content = guide_bytes if guide_bytes is not None else (ROOT / 'templates/project/BOOTSTRAP.md').read_bytes()
    payloads = {guide: content, 'BOOTSTRAP.md': POINTER}
    if mode != 'upgrade':
        baseline = git(root, 'rev-parse', 'HEAD').decode().strip() if (root / '.git').exists() and has_head(root) else None
        state = envelope(initial_snapshot(project_id, owner, baseline, guide, hashlib.sha256(content).hexdigest()))
        payloads['.ai-org/state.json'] = canonical(state) + b'\n'
    rows = file_plan(root, [{'target': path, 'sha256': hashlib.sha256(data).hexdigest()} for path, data in sorted(payloads.items())])
    result = dict(format='project-plan/1', operation_id=uuid.uuid4().hex, mode=mode, version=version,
                  target=str(root), before=fingerprint(inventory(root)), previous=previous, guide=guide,
                  source_sha256=fingerprint({p: hashlib.sha256(b).hexdigest() for p, b in payloads.items()}),
                  files=rows, payloads={p: base64.b64encode(b).decode() for p, b in payloads.items()})
    result['plan_sha256'] = fingerprint(result)
    return result


def verify_plan(proposed, supplied_hash):
    from jsonschema import Draft202012Validator
    errors = list(Draft202012Validator(load_json(ROOT / 'schemas/install-plan.schema.json')).iter_errors(proposed))
    if errors: raise ValueError('invalid plan: ' + errors[0].message)
    body = {k: v for k, v in proposed.items() if k != 'plan_sha256'}
    if supplied_hash != proposed['plan_sha256'] or supplied_hash != fingerprint(body): raise ValueError('plan fingerprint mismatch')
    # The apply API accepts only the fixed project asset set, never arbitrary writes.
    allowed = {proposed['guide'], 'BOOTSTRAP.md'}
    if proposed['mode'] != 'upgrade': allowed.add('.ai-org/state.json')
    if proposed['guide'] != '.ai-org/versions/' + proposed['version'] + '/BOOTSTRAP.md': raise ValueError('invalid guide path')
    if set(proposed['payloads']) != allowed or {r['path'] for r in proposed['files']} != allowed or len(proposed['files']) != len(allowed):
        raise ValueError('invalid plan paths')
    data = {k: base64.b64decode(v, validate=True) for k, v in proposed['payloads'].items()}
    if proposed['source_sha256'] != fingerprint({p: hashlib.sha256(b).hexdigest() for p, b in data.items()}):
        raise ValueError('source fingerprint mismatch')
    for row in proposed['files']:
        if hashlib.sha256(data[row['path']]).hexdigest() != row['sha256']: raise ValueError('payload fingerprint mismatch')
    if data['BOOTSTRAP.md'] != POINTER: raise ValueError('invalid bootstrap pointer')
    if '.ai-org/state.json' in data:
        state = json.loads(data['.ai-org/state.json']); idle(state)
        if state['operations'] or state['snapshot']['authorizations'] or state['snapshot']['workers'] or any(
                w['state'] != 'planned' for w in state['snapshot']['work_packages']):
            raise ValueError('installation cannot grant execution rights')
        errors = validate(state['snapshot'], now())
        if errors: raise ValueError('; '.join(errors))
    return data


def apply(root, proposed, supplied_hash, fault=None):
    root = root_path(root)
    data = verify_plan(proposed, supplied_hash)
    if proposed['target'] != str(root): raise ValueError('plan target mismatch')
    journal_path = safe_path(root, '.ai-org/install-journal.json')
    receipt_dir = safe_path(root, '.ai-org/installations')
    receipt_path = safe_path(root, '.ai-org/installations/' + proposed['operation_id'] + '.json')
    with authority_lock(root, create=True):
        if receipt_path.exists():
            old = load_json(receipt_path)
            if old['plan_sha256'] != supplied_hash: raise ValueError('operation_id reused')
            if old['state'] != 'committed': raise ValueError('installation incomplete or rolled back; preserve and reconcile')
            journal = load_json(journal_path)
            if journal['transaction_id'] == old['transaction_id'] and journal['state'] == 'preparing':
                for row in old['created']:
                    target = safe_path(root, row['path'])
                    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != row['sha256']:
                        raise ValueError('committed installation differs; preserve for reconciliation')
                atomic_json(journal_path, dict(state='committed', transaction_id=old['transaction_id'], guide=old['guide']))
            elif journal['state'] not in ('committed', 'rolled_back'):
                raise ValueError('another installation outcome is unresolved')
            return dict(old, replayed=True)
        check_install_journal(root)
        if fingerprint(inventory(root)) != proposed['before']: raise ValueError('stale plan; target changed')
        if any(r['action'] == 'conflict' for r in proposed['files']): raise ValueError('conflicting project files')
        expected = file_plan(root, [{'target': p, 'sha256': hashlib.sha256(b).hexdigest()} for p, b in sorted(data.items())])
        if expected != proposed['files']: raise ValueError('file plan differs from target')
        if proposed['mode'] == 'upgrade': idle(load_json(safe_path(root, '.ai-org/state.json')))
        receipt_dir.mkdir(parents=True, exist_ok=True)
        history = read_receipts(receipt_dir)
        pending = [r for r in proposed['files'] if r['action'] == 'create']
        paths = {r['path'] for r in pending}
        receipt = dict(version=2, transaction_id=proposed['operation_id'], state='preparing',
                       predecessors=[r['transaction_id'] for r in history if claimed_paths(r) & paths],
                       planned=pending, created=[], created_dirs=[], plan_sha256=supplied_hash,
                       previous=proposed['previous'], guide=proposed['guide'], template_version=proposed['version'])
        atomic_json(journal_path, dict(state='preparing', transaction_id=receipt['transaction_id'], guide=proposed['guide']))
        atomic_json(receipt_path, receipt)
        if fault: fault('intent_saved')
        for row in pending:
            target = safe_path(root, row['path'])
            missing = []; parent = target.parent
            while not parent.exists(): missing.append(parent); parent = parent.parent
            for parent in reversed(missing):
                parent.mkdir(); receipt['created_dirs'].append(parent.relative_to(root).as_posix())
            with os.fdopen(os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), 'wb') as out:
                out.write(data[row['path']]); out.flush(); os.fsync(out.fileno())
            if fault: fault('file_written')
            receipt['created'].append({'path': row['path'], 'sha256': row['sha256']})
            atomic_json(receipt_path, receipt)
        receipt['state'] = 'committed'; atomic_json(receipt_path, receipt)
        if fault: fault('receipt_committed')
        atomic_json(journal_path, dict(state='committed', transaction_id=receipt['transaction_id'], guide=proposed['guide']))
        return receipt


def rollback(root, operation_id, fault=None):
    root = root_path(root)
    if not re.fullmatch('[0-9a-f]{32}', operation_id): raise ValueError('invalid transaction ID')
    with authority_lock(root):
        directory = safe_path(root, '.ai-org/installations')
        history = read_receipts(directory)
        receipt = next((r for r in history if r['transaction_id'] == operation_id), None)
        if receipt is None: raise ValueError('unknown installation')
        journal_path = safe_path(root, '.ai-org/install-journal.json')
        journal = load_json(journal_path)
        if receipt['state'] == 'rolled_back':
            if journal['transaction_id'] == operation_id and journal['state'] == 'rolling_back':
                if any(safe_path(root, r['path']).exists() for r in receipt['created']):
                    raise ValueError('unexpected files after recorded rollback')
                atomic_json(journal_path, receipt['previous'] or dict(state='rolled_back', transaction_id=operation_id, guide=None))
            return receipt
        if journal['transaction_id'] != operation_id: raise ValueError('newer installation owns current selection')
        state_path = safe_path(root, '.ai-org/state.json')
        if state_path.exists():
            state = load_json(state_path); idle(state)
            removing = {r['path'] for r in receipt['created']}
            if '.ai-org/state.json' not in removing and any(ref['path'] in removing
                    for wp in state['snapshot']['work_packages'] for ref in wp['spec_refs']):
                raise ValueError('authority still references an installed asset')
        allowed = {'BOOTSTRAP.md', '.ai-org/state.json', receipt['guide']}
        # V3 v2 receipt ownership and unknown-write checks are reused unchanged.
        rollback_files(root, receipt, allowed, history, dry_run=True)
        atomic_json(journal_path, dict(journal, state='rolling_back'))
        rollback_files(root, receipt, allowed, history)
        atomic_json(directory / (operation_id + '.json'), receipt)
        if fault: fault('rollback_recorded')
        atomic_json(journal_path, receipt['previous'] or dict(state='rolled_back', transaction_id=operation_id, guide=None))
        return receipt
