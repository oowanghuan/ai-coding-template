"""Trusted single-host checkpoint and handoff integration; no provider-name branches.

Pins and observations live in the same local authority. This is not remote worker
authentication. Actual stop must be observed through an owned process handle.
"""
import copy
import hashlib
import os
from pathlib import Path
import uuid

from framework.local.storage import authority_lock, atomic_json, fingerprint, safe_path
from framework.local.store import Store, find, now, shape, UNKNOWN
from framework.local import lifecycle
from framework.local.runner import git, workspace_entries, prepare, verify_workspace
from framework.core.protocol import validate, within
from framework.recovery.checkpoint import create_snapshot, load_snapshot, restore_snapshot


def binding(wp):
    return fingerprint({key: wp[key] for key in ('baseline_sha', 'spec_refs', 'allowed_paths',
        'forbidden_paths', 'authorization_ref', 'risk', 'accountable_role', 'external_effects')})


def commit(store, state, action, result):
    state['revision'] += 1
    state['snapshot']['project']['revision'] += 1
    operation_id = action + ':' + uuid.uuid4().hex
    state['operations'][operation_id] = dict(intent=fingerprint(result), action=action,
        actor='trusted-local-supervisor', at=now(), status='committed', result=result, revision=state['revision'])
    errors = validate(state['snapshot'], now())
    if errors:
        raise ValueError('; '.join(errors))
    shape(state)
    atomic_json(store.path, state)
    return result


def assigned(state, credentials, actor):
    if type(credentials['token']) is not int or type(credentials['epoch']) is not int:
        raise ValueError('epoch/token must be integers')
    assignment = find(state['snapshot']['assignments'], credentials['assignment_id'])
    worker = find(state['snapshot']['workers'], assignment['worker_ref'])
    wp = find(state['snapshot']['work_packages'], assignment['wp_ref'])
    if (actor != worker['principal'] or credentials['token'] != assignment['fencing_token'] or
        credentials['epoch'] != assignment['authority_epoch'] or
        assignment['authority_epoch'] != state['snapshot']['project']['authority_epoch'] or
        wp['assignment_ref'] != assignment['id']):
        raise ValueError('handoff ownership binding changed')
    return assignment, worker, wp, state['workspaces'][assignment['workspace_id']]


def checkpoint(root, credentials, actor, *, completed=(), remaining=(), evidence_refs=()):
    store = Store(root)
    with authority_lock(store.root):
        state = store._read()
        assignment, worker, wp, workspace = assigned(state, credentials, actor)
        source = safe_path(store.root, workspace['path'])
        verify_workspace(store.root, workspace)
        baseline = {path: {'sha256': hashlib.sha256(git(store.root, 'cat-file', 'blob', blob)).hexdigest(),
                           'mode': mode} for mode, blob, path in workspace_entries(store.root, assignment['base_sha'])}
        cp_id = 'checkpoint-' + uuid.uuid4().hex
        context = dict(wp_ref=wp['id'], assignment_ref=assignment['id'],
            authority_epoch=assignment['authority_epoch'], fencing_token=assignment['fencing_token'],
            baseline_sha=assignment['base_sha'], last_valid_commit=git(source, 'rev-parse', 'HEAD').decode().strip(),
            completed=list(completed), remaining=list(remaining),
            unknown_operations=copy.deepcopy((workspace['run'] or {}).get('unknown_operations', [])),
            spec_refs=wp['spec_refs'], authorization_ref=wp['authorization_ref'],
            role_ref=assignment['role_ref'], evidence_refs=list(evidence_refs),
            lease_expires_at=assignment['lease_expires_at'], binding=binding(wp))
        parent = safe_path(store.root, '.ai-org/checkpoints')
        parent.mkdir(mode=0o700, exist_ok=True)
        receipt = create_snapshot(source, parent / cp_id, context, baseline)
        record = dict(path='.ai-org/checkpoints/' + cp_id, manifest_sha256=receipt['manifest_sha256'],
                      binding=binding(wp), unknown_digest=fingerprint(context['unknown_operations']))
        workspace['checkpoint'] = record
        cp = dict(id=cp_id, wp_ref=wp['id'], wp_revision=wp['revision'], role_ref=assignment['role_ref'],
            authorization_ref=wp['authorization_ref'], assignment_ref=assignment['id'],
            lease_expires_at=assignment['lease_expires_at'], created_at=now(), spec_refs=wp['spec_refs'],
            baseline_sha=assignment['base_sha'], last_valid_commit=context['last_valid_commit'],
            uncommitted=[{'location': record['path'], 'sha256': record['manifest_sha256']}],
            completed=list(completed), remaining=list(remaining), evidence_refs=list(evidence_refs),
            decision_refs=[], blockers=[], unknown_operations=context['unknown_operations'],
            next_actions=['Reconcile exact current authority and stopped writer before handoff'])
        state['snapshot']['checkpoints'].append(cp)
        assignment['last_checkpoint'] = cp_id
        wp['checkpoint_ref'] = cp_id
        return commit(store, state, 'checkpoint', dict(checkpoint_id=cp_id, **record))


def confirm_stopped(root, credentials, actor, process):
    """Accept an owned Popen after wait; never an untrusted JSON 'stopped' flag.

    The reviewed launcher must have used start_new_session and a policy denying
    process escape. A live process group is unresolved even if its leader exited.
    """
    status = process.poll()
    if status is None:
        raise ValueError('writer still running')
    process.wait(timeout=0)
    try:
        os.killpg(process.pid, 0)
    except ProcessLookupError:
        pass
    else:
        raise ValueError('process group still has writers')
    store = Store(root)
    with authority_lock(store.root):
        state = store._read()
        assignment, worker, wp, workspace = assigned(state, credentials, actor)
        run = workspace['run'] or {}
        if run.get('pid') != process.pid or run.get('process_group') != process.pid:
            raise ValueError('owned process is not registered execution')
        if not workspace.get('checkpoint'):
            raise ValueError('preserve checkpoint before releasing unknown execution')
        checked_checkpoint(store.root, state, wp, workspace)
        workspace['state'] = 'stopped'
        workspace['run'] = dict(run, state='stopped', exit_code=status)
        if 'worker_runtime' in state:
            others = any(w['state'] in UNKNOWN and
                         find(state['snapshot']['assignments'], w['assignment_id'])['worker_ref'] == worker['id']
                         for w in state['workspaces'].values())
            state['worker_runtime']['workers'][worker['id']]['stop_confirmed'] = not others
            lifecycle.refresh(state, worker['id'])
        return commit(store, state, 'confirmed-stop', {'assignment_id': assignment['id'], 'exit_code': status})


def checked_checkpoint(root, state, wp, workspace):
    record = workspace['checkpoint']
    if record['binding'] != binding(wp):
        raise ValueError('baseline/spec/scope changed since checkpoint')
    if record['unknown_digest'] != fingerprint((workspace['run'] or {}).get('unknown_operations', [])):
        raise ValueError('new unknown operation since checkpoint')
    manifest = load_snapshot(safe_path(root, record['path']), record['manifest_sha256'])
    context = manifest['context']
    old = find(state['snapshot']['assignments'], workspace['assignment_id'])
    latest = find(state['snapshot']['checkpoints'], old['last_checkpoint'])
    if (context['assignment_ref'] != old['id'] or context['wp_ref'] != wp['id'] or
        context['fencing_token'] != old['fencing_token'] or context['authority_epoch'] != old['authority_epoch'] or
        latest['uncommitted'] != [{'location': record['path'], 'sha256': record['manifest_sha256']}]):
        raise ValueError('latest checkpoint/assignment pin mismatch')
    if context['unknown_operations']:
        raise ValueError('unknown operations require reconciliation before handoff')
    return manifest


def prepare_handoff(root, credentials, actor, expected_revision, operation_id):
    """Restore into a fresh registered worktree; never overwrite the old workspace."""
    store = Store(root)
    before = store.inspect()['state']
    new = find(before['snapshot']['assignments'], credentials['assignment_id'])
    target = before['workspaces'][new['workspace_id']]
    if not target.get('recovery_source'):
        return prepare(root, credentials, actor, expected_revision, operation_id)
    # Persist execution intent first, then keep state locked through content restore.
    result = prepare(root, credentials, actor, expected_revision, operation_id)
    with authority_lock(store.root):
        state = store._read()
        new, wp, worker = store._credential(state, credentials, actor, now(), states=('active',))
        target = state['workspaces'][new['workspace_id']]
        if target.get('restored'):
            return result
        target['state'] = 'creating'
        commit(store, state, 'restore-intent', {'assignment_id': new['id'], 'source': target['recovery_source']})
        old_workspace = state['workspaces'][target['recovery_source']]
        if old_workspace['state'] != 'stopped':
            raise ValueError('old writer stop unconfirmed')
        manifest = checked_checkpoint(store.root, state, wp, old_workspace)
        source = old_workspace['checkpoint']
        artifact = safe_path(store.root, '.ai-org/checkpoints/restore-' + uuid.uuid4().hex)
        restore_snapshot(safe_path(store.root, source['path']), source['manifest_sha256'], artifact)
        dest = verify_workspace(store.root, target, pristine=True)
        # Only changed assigned files may be restored. Validate all changes before writing.
        baseline = {path: (mode, git(store.root, 'cat-file', 'blob', blob))
                    for mode, blob, path in workspace_entries(store.root, new['base_sha'])}
        files = {str(p.relative_to(artifact)): p for p in artifact.rglob('*') if p.is_file()}
        edits = []
        for relative in sorted(set(baseline) | set(files)):
            item = files.get(relative)
            content = item.read_bytes() if item else None
            mode = '100755' if item and item.stat().st_mode & 0o111 else '100644'
            if baseline.get(relative) == (mode, content):
                continue
            if (not any(within(relative, p) for p in new['allowed_paths']) or
                any(within(relative, p) for p in wp['forbidden_paths'])):
                raise ValueError('checkpoint modifications exceed new scope')
            edits.append((relative, content, mode))
        for relative, content, mode in edits:
            path = safe_path(dest, relative)
            if content is None:
                path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                path.chmod(0o700 if mode == '100755' else 0o600)
        target['restored'] = {'manifest_sha256': source['manifest_sha256'], 'changed_paths': [e[0] for e in edits]}
        target['state'] = 'prepared'
        commit(store, state, 'restore-handoff', dict(assignment_id=new['id'], **target['restored']))
    return result
