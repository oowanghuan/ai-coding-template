"""Finite stdlib collector: deploy only independently reviewed, pinned bytes.

No candidate imports, shell, network or credential propagation. A protected plan
selects one immutable Python stdio subject; every invocation is separately sandboxed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time
import uuid

ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')
HASH = re.compile(r'[0-9a-f]{64}\Z')
GIT = re.compile(r'[0-9a-f]{40}\Z')
LOG_LIMIT = 1024 * 1024
# Darwin SDK sys/fcntl.h defines O_SEARCH as O_EXEC (0x40000000) | O_DIRECTORY.
# Python 3.9 does not expose it. Search-only FDs pin ancestors without asking
# Seatbelt for permission to read/list directories outside the allowed subtree.
DIRECTORY_ACCESS = 0x40000000 if sys.platform == 'darwin' else getattr(os, 'O_PATH', os.O_RDONLY)


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def constant(value): raise ValueError('nonfinite JSON number')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def fields(value, names):
    if type(value) is not dict or set(value) != set(names.split()):
        raise ValueError('unexpected or missing fields')


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high: raise ValueError('integer outside bounds')


def regular(path, limit=16 * 1024 * 1024):
    """Pin every directory before opening the leaf; never follow link ancestors."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts or path.resolve() != path:
        raise ValueError('canonical absolute path required')
    parent = os.open('/', DIRECTORY_ACCESS | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, DIRECTORY_ACCESS | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent); parent = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
                raise ValueError('bounded single-link regular file required')
            with os.fdopen(fd, 'rb', closefd=False) as stream: data = stream.read(limit + 1)
            if len(data) > limit: raise ValueError('file grew beyond bound')
            return data, info
        finally: os.close(fd)
    finally: os.close(parent)


def directory(value):
    path = Path(value)
    if not path.is_absolute() or path.resolve() != path or not path.is_dir():
        raise ValueError('existing canonical directory required')
    for p in (path, *path.parents):
        if p.is_symlink(): raise ValueError('linked directory')
    return path


def relative(value):
    if (type(value) is not str or not value or value.startswith('/') or '\\' in value or
            any(p in ('', '.', '..', '.git', '.ai-org') for p in value.split('/')) or '\x00' in value):
        raise ValueError('unsafe relative path')
    value.encode('utf-8')
    return value


def git_object(kind, data):
    return hashlib.sha1(kind.encode() + b' ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def tree_hash(tree):
    entries = []
    for name, value in tree.items():
        if isinstance(value, dict):
            mode, sha, ordering = '40000', tree_hash(value), name.encode() + b'/'
        else:
            mode, sha = value; ordering = name.encode()
        entries.append((ordering, mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(sha)))
    return git_object('tree', b''.join(row[1] for row in sorted(entries)))


def verify_source(plan):
    root = directory(plan['subject_root']); manifest = plan['manifest']; actual = set(); total = 0
    if type(manifest) is not dict or not 1 <= len(manifest) <= 1024:
        raise ValueError('bounded nonempty source manifest required')
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            if (Path(parent) / name).is_symlink(): raise ValueError('linked source directory')
        for name in files: actual.add(str((Path(parent) / name).relative_to(root)))
    if actual != set(manifest): raise ValueError('source file set changed')
    if len({p.casefold() for p in manifest}) != len(manifest): raise ValueError('case-alias source paths')
    tree = {}
    for name, record in sorted(manifest.items()):
        relative(name); fields(record, 'sha256 mode')
        if record['mode'] not in ('100644', '100755'): raise ValueError('unsupported source mode')
        data, info = regular(root / name); total += len(data)
        if total > 64 * 1024 * 1024: raise ValueError('source snapshot exceeds bound')
        mode = '100755' if info.st_mode & stat.S_IXUSR else '100644'
        if mode != record['mode'] or digest(data) != record['sha256']: raise ValueError('source bytes/mode changed')
        node = tree; parts = name.split('/')
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict): raise ValueError('source path collision')
        node[parts[-1]] = (mode, git_object('blob', data))
    subject = plan['subject']; fields(subject, 'commit tree manifest_sha256')
    if not GIT.fullmatch(subject['commit']) or not GIT.fullmatch(subject['tree']): raise ValueError('invalid Git identity')
    commit = plan['commit_object'].encode()
    if len(commit) > 65536 or git_object('commit', commit) != subject['commit']:
        raise ValueError('commit object mismatch')
    headers = commit.split(b'\n\n', 1)[0].splitlines()
    if [line for line in headers if line.startswith(b'tree ')] != [b'tree ' + subject['tree'].encode()]:
        raise ValueError('commit tree header mismatch')
    if tree_hash(tree) != subject['tree'] or digest(canonical(manifest)) != subject['manifest_sha256']:
        raise ValueError('Git tree/manifest mismatch')


def validate(plan):
    fields(plan, 'format run_id wp_id wp_revision kind trusted_root scratch_root subject_root entrypoint subject commit_object manifest collector_sha256 environment tests')
    if plan['format'] != 'quality-plan/1': raise ValueError('unsupported plan')
    if any(type(plan[k]) is not str or not ID.fullmatch(plan[k]) for k in ('run_id', 'wp_id')):
        raise ValueError('invalid run/work identity')
    integer(plan['wp_revision'], 1, 2**31)
    if plan['kind'] not in ('code', 'document'): raise ValueError('unsupported task kind')
    trusted, scratch, source = (directory(plan[k]) for k in ('trusted_root', 'scratch_root', 'subject_root'))
    if trusted == scratch or trusted in scratch.parents or scratch in trusted.parents:
        raise ValueError('trusted and writable roots overlap')
    if source.parent != trusted or source.name != 'subject': raise ValueError('subject must be T/subject')
    if relative(plan['entrypoint']) not in plan['manifest'] or not plan['entrypoint'].endswith('.py'):
        raise ValueError('fixed Python entrypoint missing')
    if not HASH.fullmatch(plan['collector_sha256']): raise ValueError('invalid collector hash')
    fields(plan['environment'], 'platform python python_version sandbox')
    if (plan['environment']['platform'] != 'darwin' or plan['environment']['python'] != '/usr/bin/python3'
            or plan['environment']['sandbox'] != 'macos-seatbelt'):
        raise ValueError('unsupported execution environment')
    if type(plan['tests']) is not list or len(plan['tests']) > 32: raise ValueError('too many tests')
    ids = set(); budget = 0
    for case in plan['tests']:
        fields(case, 'id required input expected_exit expected_stdout_sha256 timeout_seconds skip_reason')
        if type(case['id']) is not str or not ID.fullmatch(case['id']) or case['id'] in ids:
            raise ValueError('invalid/duplicate case ID')
        ids.add(case['id']); integer(case['expected_exit'], 0, 255); integer(case['timeout_seconds'], 1, 30)
        budget += case['timeout_seconds']
        if type(case['required']) is not bool or type(case['input']) is not str or len(case['input'].encode()) > 65536:
            raise ValueError('invalid case input')
        if not HASH.fullmatch(case['expected_stdout_sha256']): raise ValueError('invalid oracle')
        if case['skip_reason'] is not None and (type(case['skip_reason']) is not str or not case['skip_reason'].strip()):
            raise ValueError('invalid skip declaration')
    if budget > 120: raise ValueError('finite batch timeout budget exceeded')
    verify_source(plan)
    return plan


def exclusive(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream: stream.write(data); stream.flush(); os.fsync(stream.fileno())


def save_new(path, value):
    exclusive(path, canonical(value) + b'\n')
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try: os.fsync(fd)
    finally: os.close(fd)


def policy(source, scratch, writable_anchor):
    q = lambda p: json.dumps(str(p))
    runtime = ['/System', '/usr', '/bin', '/Library/Developer', '/Library/Apple',
               '/private/preboot/Cryptexes', '/private/var/db/dyld', source, scratch]
    return '\n'.join(['(version 1)', '(deny default)', '(allow process-exec)', '(deny process-fork)',
        '(deny process-info* (target others))', '(allow file-read-metadata)', '(allow file-map-executable)',
        '(allow mach-lookup (global-name "com.apple.system.logger"))',
        '(allow file-read* (literal "/") (literal "/dev/null") (literal "/dev/urandom") ' +
        ' '.join('(subpath ' + q(p) + ')' for p in runtime) + ')',
        '(allow file-write* (literal "/dev/null") (require-all (subpath ' + q(writable_anchor) +
        ') (subpath ' + q(scratch) + ')))',
        '(deny file-write-unlink (literal ' + q(writable_anchor) + ') (literal ' + q(scratch) + '))']) + '\n'


def stop(process):
    """Only this invocation's owned live child; no persisted PID signalling."""
    if process.poll() is not None: return
    os.killpg(process.pid, signal.SIGTERM)
    try: process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=2)


def run_case(plan, case):
    trusted = Path(plan['trusted_root']); scratch = Path(plan['scratch_root']) / case['id']
    command = ['/usr/bin/python3', '-I', '-B', '-S', str(Path(plan['subject_root']) / plan['entrypoint'])]
    row = dict(id=case['id'], required=case['required'], status='not_run', exit_code=None, signal=None,
        timed_out=False, output_limit_exceeded=False, collection_error=None, command=command, pid=None,
        cwd=str(scratch), input_sha256=digest(case['input'].encode()), expected_exit=case['expected_exit'],
        expected_stdout_sha256=case['expected_stdout_sha256'], stdout=None, stderr=None,
        policy_sha256=None, skip_reason=case['skip_reason'], started_at=None, finished_at=None)
    if case['skip_reason'] is not None: row['status'] = 'skipped'; return row
    scratch.mkdir(mode=0o700)
    policy_path = trusted / 'policies' / (case['id'] + '.sb')
    rules = policy(plan['subject_root'], scratch, plan['scratch_root']).encode()
    exclusive(policy_path, rules); row['policy_sha256'] = digest(rules)
    env = dict(HOME=str(scratch), TMPDIR=str(scratch), PATH='/usr/bin:/bin',
               PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1')
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}; proc = None
    row['started_at'] = utc()
    try:
        proc = subprocess.Popen(['/usr/bin/sandbox-exec', '-f', str(policy_path)] + command,
            cwd=scratch, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True, close_fds=True)
        row['pid'] = proc.pid; data = case['input'].encode(); offset = 0
        deadline = time.monotonic() + case['timeout_seconds']
        with selectors.DefaultSelector() as selector:
            for name in ('stdout', 'stderr'):
                stream = getattr(proc, name); os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, name)
            os.set_blocking(proc.stdin.fileno(), False)
            if data: selector.register(proc.stdin, selectors.EVENT_WRITE, 'stdin')
            else: proc.stdin.close()
            while selector.get_map():
                if time.monotonic() >= deadline:
                    row['timed_out'] = True; stop(proc); deadline = time.monotonic() + 2
                for key, _ in selector.select(timeout=0.05):
                    if key.data == 'stdin':
                        try: offset += os.write(key.fd, data[offset:offset + 16384])
                        except BlockingIOError: continue
                        except BrokenPipeError: offset = len(data)
                        if offset == len(data): selector.unregister(key.fileobj); key.fileobj.close()
                    else:
                        try: part = os.read(key.fd, 16384)
                        except BlockingIOError: continue
                        if not part: selector.unregister(key.fileobj); key.fileobj.close(); continue
                        buf = buffers[key.data]; remaining = LOG_LIMIT - len(buf)
                        buf.extend(part[:remaining])
                        if len(part) > remaining:
                            row['output_limit_exceeded'] = True; stop(proc)
                if proc.poll() is not None and proc.stdin and not proc.stdin.closed:
                    if proc.stdin in selector.get_map(): selector.unregister(proc.stdin)
                    proc.stdin.close()
            try: proc.wait(timeout=max(0.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                row['timed_out'] = True; stop(proc)
    except BaseException as error:
        row['collection_error'] = type(error).__name__ + ': ' + str(error)[:200]
        if proc is not None:
            try: stop(proc)
            except BaseException: row['collection_error'] += '; process stop not confirmed'
    finally:
        if proc is not None:
            row['exit_code'] = proc.poll()
            for name in ('stdin', 'stdout', 'stderr'):
                stream = getattr(proc, name)
                if stream is not None and not stream.closed: stream.close()
        row['finished_at'] = utc()
    if row['exit_code'] is not None and row['exit_code'] < 0: row['signal'] = -row['exit_code']
    for name, data in buffers.items():
        path = 'logs/' + case['id'] + '.' + name
        exclusive(trusted / path, bytes(data)); row[name] = dict(path=path, size=len(data), sha256=digest(data))
    if row['exit_code'] is not None:
        row['status'] = 'passed' if (not row['timed_out'] and not row['output_limit_exceeded'] and
            row['collection_error'] is None and row['signal'] is None and
            row['exit_code'] == case['expected_exit'] and row['stdout']['sha256'] == case['expected_stdout_sha256']) else 'failed'
    return row


def collect(plan_path, expected_plan_sha):
    raw, _ = regular(plan_path)
    if digest(raw) != expected_plan_sha: raise ValueError('plan pin mismatch')
    plan = validate(strict_json(raw)); trusted = Path(plan['trusted_root'])
    if Path(plan_path) != trusted / 'plan.json' or Path(__file__).resolve().parent != trusted:
        raise ValueError('execute only protected T/collector.py with T/plan.json')
    program, _ = regular(Path(__file__).resolve())
    if digest(program) != plan['collector_sha256']: raise ValueError('collector pin mismatch')
    if sys.platform != 'darwin': raise ValueError('unsupported OS; no unsandboxed fallback')
    version = subprocess.run(['/usr/bin/python3', '--version'], env={'PATH': '/usr/bin:/bin',
        'HOME': str(trusted), 'TMPDIR': str(plan['scratch_root'])}, capture_output=True, timeout=5, check=True)
    actual_version = version.stdout.decode().strip().removeprefix('Python ')
    environment = dict(platform=sys.platform, python='/usr/bin/python3', python_version=actual_version, sandbox='macos-seatbelt')
    if environment != plan['environment']: raise ValueError('environment pin mismatch')
    save_new(trusted / 'intent.json', dict(run_id=plan['run_id'], plan_sha256=expected_plan_sha,
        collector_sha256=digest(program), started_at=utc()))
    (trusted / 'logs').mkdir(mode=0o700); (trusted / 'policies').mkdir(mode=0o700)
    result = dict(format='quality-evidence/1', evidence_id=plan['run_id'], wp_id=plan['wp_id'],
        wp_revision=plan['wp_revision'], kind=plan['kind'], subject=plan['subject'], plan_sha256=expected_plan_sha,
        collector_sha256=digest(program), adapter='python-stdio/1', state='unknown', started_at=utc(),
        finished_at=None, environment=environment, source_unchanged=False, cases=[], counts={})
    try:
        for case in plan['tests']:
            row = run_case(plan, case); result['cases'].append(row)
            if row['collection_error'] is not None or (row['exit_code'] is None and row['status'] != 'skipped'):
                break  # An interrupted/unknown run never starts another case.
        verify_source(plan); result['source_unchanged'] = True
        if len(result['cases']) == len(plan['tests']) and all(c['collection_error'] is None and
                (c['exit_code'] is not None or c['status'] == 'skipped') for c in result['cases']):
            result['state'] = 'complete'
    finally:
        result['finished_at'] = utc()
        result['counts'] = {name: sum(c['status'] == name for c in result['cases'])
                            for name in ('passed', 'failed', 'skipped', 'not_run')}
        save_new(trusted / 'evidence.json', result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--plan-sha256', required=True); a = p.parse_args()
    result = collect(a.plan, a.plan_sha256)
    print(json.dumps({'run_id': result['evidence_id'], 'state': result['state'], 'counts': result['counts']}))
    return 0 if result['state'] == 'complete' else 2


if __name__ == '__main__':
    try: sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr); sys.exit(2)
