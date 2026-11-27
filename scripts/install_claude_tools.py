#!/usr/bin/env python3
"""Install the preserved V3 tool definitions; not a V4 agent or project bootstrap."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'manifests/v3-tools.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('Invalid relative path')
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ('', '.', '..') for x in value.split('/')):
        raise ValueError('Unsafe path: ' + value)
    return p


def checked_path(root, value):
    p = root
    for part in relative(value).parts:
        p = p / part
        if p.is_symlink():
            raise ValueError('Symlink refused: ' + value)
    if not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path leaves root: ' + value)
    return p


def load_manifest():
    manifest = json.loads(MANIFEST.read_text())
    if manifest['version'] != 1:
        raise ValueError('Unsupported tool manifest version')
    ids, targets = set(), set()
    for row in manifest['tools'] + manifest['resources']:
        relative(row['target'])
        if relative(row['target']).parts[0] in ('.git', '.ai-coding-template'):
            raise ValueError('Reserved target')
        if row['target'] in targets:
            raise ValueError('Duplicate target')
        targets.add(row['target'])
        source = checked_path(ROOT, row['source'])
        if not source.is_file() or digest(source.read_bytes()) != row['sha256']:
            raise ValueError('Missing or changed canonical source: ' + row['source'])
        if 'id' in row:
            if row['id'] in ids:
                raise ValueError('Duplicate tool ID')
            ids.add(row['id'])
    for row in manifest['tools']:
        if not set(row['requires']) <= ids:
            raise ValueError('Missing tool dependency: ' + row['id'])
    for row in manifest['preserved_copies']:
        p = checked_path(ROOT, row['path'])
        if digest(p.read_bytes()) != row['sha256']:
            raise ValueError('Unreviewed compatibility-copy change: ' + row['path'])
    return manifest


def selection(manifest, groups):
    tools = {r['id']: r for r in manifest['tools']}
    selected = {r['id'] for r in tools.values() if r['kind'] in groups}
    while True:
        expanded = selected | {dep for name in selected for dep in tools[name]['requires']}
        if expanded == selected:
            break
        selected = expanded
    # Commands read these preserved framework templates. No GUI backup or executable hooks.
    return [tools[name] for name in sorted(selected)] + manifest['resources']


def plan(target, rows):
    result = []
    for row in rows:
        p = checked_path(target, row['target'])
        status = 'create'
        if p.exists():
            status = 'unchanged' if p.is_file() and digest(p.read_bytes()) == row['sha256'] else 'conflict'
        # Reject non-directory ancestors before any write.
        for parent in p.parents:
            if parent == target:
                break
            if parent.exists() and not parent.is_dir():
                status = 'conflict'
        result.append({'path': row['target'], 'sha256': row['sha256'], 'action': status})
    return result


def atomic_json(path, data):
    temp = path.with_suffix('.tmp')
    if temp.is_symlink():
        raise ValueError('Symlink transaction file')
    with temp.open('w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def rollback(target, receipt, allowed):
    if receipt['state'] == 'rolled_back':
        return  # A historical receipt must not delete a later reinstallation.
    rows = receipt['created']
    if len({r['path'] for r in rows}) != len(rows):
        raise ValueError('Duplicate receipt path')
    for r in rows:
        if r['path'] not in allowed:
            raise ValueError('Receipt contains a non-manifest path')
        p = checked_path(target, r['path'])
        if p.exists() and (not p.is_file() or digest(p.read_bytes()) != r['sha256']):
            raise ValueError('Rollback preserves edited file: ' + r['path'])
    recorded = {r['path'] for r in rows}
    for r in receipt.get('planned', []):
        if r['path'] not in recorded and checked_path(target, r['path']).exists():
            raise ValueError('Unknown interrupted write; reconcile before rollback: ' + r['path'])
    for r in reversed(rows):
        p = checked_path(target, r['path'])
        if p.exists():
            p.unlink()
    # Only directories actually created by this transaction, and only if empty.
    for name in reversed(receipt.get('created_dirs', [])):
        p = checked_path(target, name)
        try:
            p.rmdir()
        except OSError:
            pass
    receipt['state'] = 'rolled_back'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--target', type=Path)
    parser.add_argument('-o', '--only', default='commands,skills,subagents')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--rollback', metavar='TRANSACTION_ID')
    args = parser.parse_args()
    manifest = load_manifest()  # List and dry-run fail on missing/changed sources too.
    groups = set(args.only.split(','))
    if not groups or not groups <= {'commands', 'skills', 'subagents'}:
        raise ValueError('Invalid --only; use commands,skills,subagents')
    rows = selection(manifest, groups)
    if args.list:
        print(json.dumps({'tools': [r['id'] for r in rows if 'id' in r],
                          'resources': len(manifest['resources']),
                          'native_loading_verified': False}, indent=2))
        return 0
    if args.target is None or not args.target.is_dir() or args.target.is_symlink():
        raise ValueError('--target must be an existing non-symlink directory')
    target = args.target.resolve()
    proposed = plan(target, rows)
    if args.dry_run:
        if args.rollback:
            raise ValueError('--dry-run and --rollback are separate operations')
        print(json.dumps({'dry_run': True, 'files': proposed}, indent=2))
        return 2 if any(r['action'] == 'conflict' for r in proposed) else 0
    if not args.rollback and any(r['action'] == 'conflict' for r in proposed):
        print(json.dumps({'error': 'conflict; no files written', 'files': proposed}, indent=2))
        return 2
    state = checked_path(target, '.ai-coding-template')
    state.mkdir(exist_ok=True)
    lock_path = checked_path(target, '.ai-coding-template/install.lock')
    with lock_path.open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        receipts = checked_path(target, '.ai-coding-template/transactions')
        receipts.mkdir(exist_ok=True)
        if args.rollback:
            if len(args.rollback) != 32 or any(c not in '0123456789abcdef' for c in args.rollback):
                raise ValueError('Invalid transaction ID')
            path = checked_path(target, '.ai-coding-template/transactions/' + args.rollback + '.json')
            receipt = json.loads(path.read_text())
            rollback(target, receipt, {r['target'] for r in manifest['tools'] + manifest['resources']})
            atomic_json(path, receipt)
            print(json.dumps({'transaction_id': args.rollback, 'state': receipt['state']}))
            return 0
        for path in receipts.glob('*.json'):
            if path.is_symlink():
                raise ValueError('Symlink receipt')
            if json.loads(path.read_text())['state'] not in ('committed', 'rolled_back'):
                raise ValueError('Incomplete transaction; inspect and rollback before installing again: ' + path.stem)
        proposed = plan(target, rows)  # Recheck under the cooperative single-host lock.
        if any(r['action'] == 'conflict' for r in proposed):
            raise ValueError('Target changed while waiting for installation lock')
        pending = [r for r in proposed if r['action'] == 'create']
        if not pending:
            print(json.dumps({'state': 'unchanged', 'created': 0}))
            return 0
        data = {r['target']: checked_path(ROOT, r['source']).read_bytes() for r in rows}
        # Source cannot silently change between validation and write.
        if any(digest(data[r['path']]) != r['sha256'] for r in pending):
            raise ValueError('Source changed during planning')
        transaction = uuid.uuid4().hex
        receipt = {'version': 1, 'transaction_id': transaction, 'state': 'preparing',
                   'manifest_sha256': digest(MANIFEST.read_bytes()), 'planned': pending,
                   'created': [], 'created_dirs': []}
        receipt_path = receipts / (transaction + '.json')
        atomic_json(receipt_path, receipt)
        try:
            for row in pending:
                p = checked_path(target, row['path'])
                absent = []
                parent = p.parent
                while not parent.exists():
                    absent.append(parent)
                    parent = parent.parent
                for parent in reversed(absent):
                    parent.mkdir()
                    receipt['created_dirs'].append(parent.relative_to(target).as_posix())
                fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o644)
                try:
                    with os.fdopen(fd, 'wb') as stream:
                        stream.write(data[row['path']])
                        stream.flush()
                        os.fsync(stream.fileno())
                except BaseException:
                    # This process just created this exclusive file; preserve ambiguous crash results.
                    receipt['state'] = 'needs_recovery'
                    atomic_json(receipt_path, receipt)
                    raise
                receipt['created'].append({'path': row['path'], 'sha256': row['sha256']})
                atomic_json(receipt_path, receipt)
            receipt['state'] = 'committed'
            atomic_json(receipt_path, receipt)
        except BaseException:
            receipt['state'] = 'needs_recovery'
            atomic_json(receipt_path, receipt)
            # Retain the receipt and files; never guess ownership after interrupted IO.
            raise
        print(json.dumps({'state': 'committed', 'transaction_id': transaction, 'created': len(pending)}))
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(2)
