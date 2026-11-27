"""macOS-only synthetic runner. No network, credentials, hooks or arbitrary commands."""
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

from framework.core.protocol import within
from framework.local.storage import safe_path
from framework.local.store import Store, find, now


def git(root, *args):
    env = {'PATH': '/usr/bin:/bin', 'HOME': '/nonexistent', 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0'}
    p = subprocess.run(['/usr/bin/git', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false',
                        '-c', 'core.untrackedCache=false', *args], cwd=root, env=env,
                       capture_output=True, timeout=30)
    if p.returncode:
        raise ValueError('local Git operation failed: ' + p.stderr.decode(errors='replace')[-500:])
    return p.stdout


def workspace_entries(root, sha):
    entries = []
    for row in git(root, 'ls-tree', '-rz', '--full-tree', sha).split(b'\0'):
        if not row:
            continue
        meta, name = row.split(b'\t', 1)
        mode, kind, blob = meta.decode().split()
        relative = name.decode('utf-8')
        safe_path(root, relative)
        if mode not in ('100644', '100755') or kind != 'blob' or relative.split('/')[0] in ('.git', '.ai-org'):
            raise ValueError('unsupported or reserved Git entry: ' + relative)
        entries.append((mode, blob, relative))
    return entries


def verify_workspace(root, workspace, pristine=False):
    path = safe_path(root, workspace['path'])
    registered = git(root, 'worktree', 'list', '--porcelain').decode()
    if 'worktree ' + str(path) + '\n' not in registered:
        raise ValueError('worktree is not registered at its exact path')
    if git(path, 'rev-parse', 'HEAD').decode().strip() != workspace['baseline_sha']:
        raise ValueError('workspace baseline mismatch')
    if pristine:
        for mode, blob, relative in workspace_entries(root, workspace['baseline_sha']):
            target = safe_path(path, relative)
            if (not target.is_file() or target.stat().st_nlink != 1 or
                    target.read_bytes() != git(root, 'cat-file', 'blob', blob) or
                    bool(target.stat().st_mode & 0o111) != (mode == '100755')):
                raise ValueError('workspace materialization incomplete or changed')
        if git(path, 'write-tree').decode().strip() != git(root, 'rev-parse', workspace['baseline_sha'] + '^{tree}').decode().strip():
            raise ValueError('workspace index incomplete or changed')
        if git(path, 'ls-files', '--others', '--exclude-standard').strip():
            raise ValueError('unexpected workspace files; preserve for inspection')
    return path


def prepare(root, credentials, actor, expected_revision, operation_id, fault=None):
    store = Store(root)
    before = store.inspect()['state']
    assignment = find(before['snapshot']['assignments'], credentials['assignment_id'])
    entries = workspace_entries(store.root, assignment['base_sha'])
    result = store.change('start', credentials, actor, expected_revision, operation_id)
    current = store.inspect()['state']
    workspace = current['workspaces'][assignment['workspace_id']]
    if result['replayed']:
        if workspace['state'] == 'prepared':
            verify_workspace(store.root, workspace)
            return result
        raise ValueError('start outcome requires reconciliation; no automatic repeat')
    if fault:
        fault('intent_saved')
    store.guard(credentials, actor)
    path = safe_path(store.root, workspace['path'])
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.exists():
        raise ValueError('workspace already exists; preserve and reconcile')
    # No checkout: repository smudge filters and post-checkout hooks never execute.
    git(store.root, 'worktree', 'add', '--detach', '--no-checkout', str(path), assignment['base_sha'])
    for mode, blob, relative in entries:
        target = safe_path(path, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(git(store.root, 'cat-file', 'blob', blob))
        target.chmod(0o755 if mode == '100755' else 0o644)
    git(path, 'reset', '--mixed', assignment['base_sha'])  # index only, no checkout/filter.
    if fault:
        fault('workspace_created')
    verify_workspace(store.root, workspace, pristine=True)
    store.workspace_phase(credentials, actor, 'creating', 'prepared')
    return result


def sandbox_policy(workspace, framework, writable, scratch):
    quote = lambda p: json.dumps(str(p))
    reads = [Path('/System'), Path('/usr'), Path('/bin'), Path('/Library/Developer'),
             Path('/Library/Apple'), Path('/private/preboot/Cryptexes'),
             Path('/private/var/db/dyld'), workspace, framework, scratch]
    return '\n'.join([
        '(version 1)', '(deny default)', '(allow process*)', '(allow sysctl-read)',
        '(allow file-read-metadata)', '(allow file-map-executable)',
        '(allow mach-lookup (global-name "com.apple.system.logger"))',
        '(allow file-read* (literal "/") (literal "/dev/null") (literal "/dev/urandom") ' +
        ' '.join('(subpath ' + quote(p) + ')' for p in reads) + ')',
        '(allow file-write* (literal "/dev/null") (subpath ' + quote(scratch) + ') (literal ' + quote(writable) + '))',
    ])


def run(root, credentials, actor, path, content, operation_id, expected_revision, delay_seconds=0, timeout=20, fault=None):
    if platform.system() != 'Darwin' or not Path('/usr/bin/sandbox-exec').exists():
        raise ValueError('supported OS sandbox unavailable; execution refused')
    if not 0 <= delay_seconds <= 30 or not 0 < timeout <= 60 or len(content.encode()) > 65536:
        raise ValueError('bounded synthetic task only')
    store = Store(root)
    payload = dict(credentials, path=path, content_sha256=hashlib.sha256(content.encode()).hexdigest(),
                   delay_seconds=delay_seconds, timeout=timeout)
    result = store.change('run-begin', payload, actor, expected_revision, operation_id)
    state = store.inspect()['state']
    assignment = find(state['snapshot']['assignments'], credentials['assignment_id'])
    wp = find(state['snapshot']['work_packages'], assignment['wp_ref'])
    workspace = state['workspaces'][assignment['workspace_id']]
    if result['replayed']:
        if workspace['state'] == 'finished':
            if workspace['run'].get('exit_code') != 0:
                raise ValueError('synthetic process failed; inspect preserved logs')
            return workspace['run']
        raise ValueError('runner outcome unresolved or stopped; do not repeat')
    if fault:
        fault('launch_intent_saved')
    store.guard(credentials, actor)
    directory = verify_workspace(store.root, workspace)
    target = safe_path(directory, path)
    if path.split('/')[0] in ('.git', '.ai-org') or not any(within(path, p) for p in assignment['allowed_paths']) or any(
            within(path, p) for p in wp['forbidden_paths']):
        raise ValueError('synthetic output outside assigned scope')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and (not target.is_file() or target.stat().st_nlink != 1):
        raise ValueError('linked/non-file output refused')
    scratch = safe_path(store.root, '.ai-org/runner/' + assignment['workspace_id'])
    scratch.mkdir(parents=True, mode=0o700, exist_ok=False)
    policy = scratch / 'policy.sb'
    policy.write_text(sandbox_policy(directory, Path(__file__).resolve().parent, target, scratch))
    marker = dict(workspace['run'], operation_id=operation_id)
    env = {'HOME': str(scratch), 'TMPDIR': str(scratch), 'PATH': '/usr/bin:/bin',
           'PYTHONNOUSERSITE': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'LANG': 'en_US.UTF-8'}
    stdout = scratch / 'stdout.log'
    stderr = scratch / 'stderr.log'
    process = None
    try:
        with stdout.open('wb') as out, stderr.open('wb') as err:
            process = subprocess.Popen(['/usr/bin/sandbox-exec', '-f', str(policy), sys.executable, '-B', '-S',
                str(Path(__file__).with_name('worker_process.py'))], cwd=directory, env=env,
                stdin=subprocess.PIPE, stdout=out, stderr=err, start_new_session=True)
            process.stdin.write(json.dumps({'path': path, 'content': content, 'delay_seconds': delay_seconds}).encode())
            process.stdin.close()
            if fault:
                fault('process_started')
            marker.update(state='running', pid=process.pid)
            store.workspace_phase(credentials, actor, 'launching', 'running', run=marker)
            deadline = time.monotonic() + timeout
            while process.poll() is None:
                store.guard(credentials, actor)
                if time.monotonic() >= deadline:
                    raise ValueError('synthetic runner timeout')
                time.sleep(0.05)
            store.guard(credentials, actor)
            marker.update(state='finished', exit_code=process.returncode,
                          stdout_sha256=hashlib.sha256(stdout.read_bytes()).hexdigest(),
                          stderr_sha256=hashlib.sha256(stderr.read_bytes()).hexdigest())
            store.workspace_phase(credentials, actor, 'running', 'finished', run=marker)
            if process.returncode:
                raise ValueError('synthetic process failed; inspect preserved logs')
    except BaseException:
        # Known parent-owned process: terminate before releasing its workspace.
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=2)
        current = store.inspect()['state']['workspaces'][assignment['workspace_id']]
        if current['state'] in ('launching', 'running'):
            marker.update(state='stopped', exit_code=process.returncode if process else None)
            store.workspace_phase(credentials, actor, current['state'], 'stopped', run=marker, allow_fenced=True)
        raise
    return marker  # Delivery is a separate fresh-credential submit operation, never automatic acceptance.
