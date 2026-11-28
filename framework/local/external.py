"""Explicit finite external launcher client; project state remains authoritative.

The coordinator provisions a pinned launcher/config and read-only receipts outside
the candidate's writable sandbox. A request is not authorization or proof of exit.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import time

from framework.local.storage import canonical, safe_path
from framework.local.store import Store, find, DIRECT_WORKSPACE_PREFIX
from framework.local.runner import verify_workspace

IDENTIFIER = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')
SHA = re.compile(r'[0-9a-f]{64}\Z')
TERMINAL = {'finished', 'stopped', 'rejected'}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def regular_bytes(path, limit=1048576):
    path = Path(path)
    if not path.is_absolute() or path.resolve() != path:
        raise ValueError('launcher paths must be canonical and not symlinks')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError('launcher file must be bounded, regular and single-link')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        if len(data) > limit: raise ValueError('launcher file exceeds bound')
        return data
    finally:
        os.close(fd)


def directory(path):
    path = Path(path)
    if not path.is_absolute() or not path.is_dir() or path.resolve() != path:
        raise ValueError('launcher directory must be existing, canonical and non-symlink')
    return path


def immutable_json(path, value):
    """Publish complete bytes once; same intent replays, different intent fails."""
    parent = directory(path.parent)
    lock_fd = os.open(parent / (path.name + '.lock'), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(lock_fd).st_mode) or os.fstat(lock_fd).st_nlink != 1:
            raise ValueError('unsafe request lock')
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        if path.exists() or path.is_symlink():
            if canonical(json.loads(regular_bytes(path))) != canonical(value):
                raise ValueError('launcher request identity already has another intent')
            return
        fd, name = tempfile.mkstemp(prefix='.request-', dir=parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(canonical(value) + b'\n'); stream.flush(); os.fsync(stream.fileno())
            os.replace(name, path)
            directory_fd = os.open(parent, os.O_RDONLY)
            try: os.fsync(directory_fd)
            finally: os.close(directory_fd)
        finally:
            if os.path.exists(name): os.unlink(name)
    finally:
        os.close(lock_fd)


class ExternalClient:
    def __init__(self, config_path, job_id, operation_id, workspace, path, content, delay_seconds, timeout):
        if any(part.casefold().startswith(DIRECT_WORKSPACE_PREFIX)
               for item in (Path(workspace), Path(workspace) / path) for part in item.parts):
            raise ValueError('external launcher cannot authorize the direct-local-only namespace')
        if not isinstance(job_id, str) or not IDENTIFIER.fullmatch(job_id):
            raise ValueError('invalid launcher job ID')
        if type(delay_seconds) is not int or type(timeout) is not int:
            raise ValueError('invalid launch timing')
        if not 0 <= delay_seconds <= 30 or not 0 < timeout <= 60 or len(content.encode()) > 65536:
            raise ValueError('bounded synthetic task only')
        raw = regular_bytes(Path(config_path))
        config = json.loads(raw)
        if config.get('format') != 'v4-launch-config/1': raise ValueError('unsupported launcher config')
        trusted = directory(config['trusted_root'])
        candidate = directory(config['candidate_root'])
        if trusted == candidate or trusted in candidate.parents or candidate in trusted.parents:
            raise ValueError('candidate and trusted roots must not overlap')
        if trusted not in Path(config_path).parents: raise ValueError('config must be inside trusted root')
        jobs = [j for j in config['jobs'] if j['job_id'] == job_id]
        if len(jobs) != 1: raise ValueError('job is not uniquely provisioned')
        job = jobs[0]
        if (job['operation_id'] != operation_id or job['workspace'] != str(workspace)
                or job['output'] != path or job['content_sha256'] != sha256(content.encode())
                or delay_seconds > job['max_delay_seconds'] or timeout > job['max_runtime_seconds']):
            raise ValueError('request differs from provisioned launch capability')
        self.requests = directory(config['request_dir'])
        self.receipts = directory(config['receipt_dir'])
        self.scratch = directory(config['scratch_root'])
        if candidate not in self.requests.parents or candidate not in Path(workspace).parents:
            raise ValueError('request/workspace outside candidate root')
        if trusted not in self.receipts.parents or trusted not in self.scratch.parents:
            raise ValueError('receipt/log directory must be inside trusted root')
        if self.requests == trusted or trusted in self.requests.parents or self.requests in trusted.parents:
            raise ValueError('requests cannot share trusted storage')
        self.job_id, self.operation_id = job_id, operation_id
        self.config_sha256 = sha256(raw)
        self.request = dict(format='v4-launch-request/1', job_id=job_id, operation_id=operation_id,
                            content=content, delay_seconds=delay_seconds, timeout=timeout)
        self.request_sha256 = sha256(canonical(self.request))
        self.last_sequence, self.last_receipt_hash, self.pid = 0, None, None

    def submit(self):
        immutable_json(self.requests / (self.job_id + '.request.json'), self.request)

    def cancel(self):
        immutable_json(self.requests / (self.job_id + '.cancel.json'),
                       dict(format='v4-launch-cancel/1', job_id=self.job_id, request_sha256=self.request_sha256))

    def status(self):
        path = self.receipts / (self.job_id + '.json')
        try: raw = regular_bytes(path)
        except FileNotFoundError: return None
        receipt = json.loads(raw)
        if (receipt.get('format') != 'v4-launch-receipt/1' or receipt.get('job_id') != self.job_id
                or receipt.get('operation_id') != self.operation_id
                or receipt.get('config_sha256') != self.config_sha256
                or receipt.get('request_sha256') != self.request_sha256):
            raise ValueError('launcher receipt input binding mismatch')
        sequence = receipt.get('sequence')
        content_hash = sha256(raw)
        if (type(sequence) is not int or sequence < 1 or sequence < self.last_sequence
                or (sequence == self.last_sequence and content_hash != self.last_receipt_hash)):
            raise ValueError('launcher receipt sequence changed or regressed')
        state = receipt.get('state')
        if state not in TERMINAL | {'launching', 'running', 'unknown'}:
            raise ValueError('invalid launcher receipt state')
        pid = receipt.get('pid')
        if state in ('running', 'finished', 'stopped'):
            if type(pid) is not int or pid < 1 or (self.pid is not None and pid != self.pid):
                raise ValueError('launcher process identity mismatch')
            self.pid = pid
        if state in ('finished', 'stopped'):
            if type(receipt.get('exit_code')) is not int:
                raise ValueError('terminal receipt has no observed exit code')
            for name in ('stdout', 'stderr'):
                expected = receipt.get(name + '_sha256')
                if not isinstance(expected, str) or not SHA.fullmatch(expected):
                    raise ValueError('terminal receipt has no log fingerprint')
                if sha256(regular_bytes(self.scratch / self.job_id / (name + '.log'))) != expected:
                    raise ValueError('launcher log fingerprint mismatch')
        if state == 'rejected' and (pid is not None or receipt.get('exit_code') is not None):
            raise ValueError('prelaunch rejection must not assert a process')
        self.last_sequence, self.last_receipt_hash = sequence, content_hash
        return receipt


def run_external(root, credentials, actor, path, content, operation_id, expected_revision,
                 config_path, job_id, delay_seconds=0, timeout=20, fault=None):
    store = Store(root)
    before = store.inspect()['state']
    assignment = find(before['snapshot']['assignments'], credentials['assignment_id'])
    workspace = before['workspaces'][assignment['workspace_id']]
    worktree = safe_path(store.root, workspace['path'])
    if any(part.casefold().startswith(DIRECT_WORKSPACE_PREFIX) for part in worktree.parts):
        raise ValueError('external launcher cannot authorize the direct-local-only namespace')
    client = ExternalClient(config_path, job_id, operation_id, worktree, path, content, delay_seconds, timeout)
    payload = dict(credentials, path=path, content_sha256=sha256(content.encode()),
                   delay_seconds=delay_seconds, timeout=timeout, backend='external',
                   launcher_job_id=job_id, launcher_config_sha256=client.config_sha256)
    result = store.change('run-begin', payload, actor, expected_revision, operation_id)
    state = store.inspect()['state']; workspace = state['workspaces'][assignment['workspace_id']]
    if result['replayed']:
        if workspace['state'] == 'finished' and workspace['run'].get('exit_code') == 0:
            return workspace['run']
        raise ValueError('external run failed or unresolved; no automatic repeat')
    marker = dict(workspace['run'], backend='external', operation_id=operation_id, job_id=job_id,
                  launcher_config_sha256=client.config_sha256, request_sha256=client.request_sha256)
    receipt = None
    try:
        store.guard(credentials, actor)
        verify_workspace(store.root, workspace)
        target = safe_path(worktree, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and (not target.is_file() or target.stat().st_nlink != 1):
            raise ValueError('linked/non-file output refused')
        store.workspace_phase(credentials, actor, 'launching', 'launching', run=marker)
        if fault: fault('launch_intent_saved')
        client.submit()
        if fault: fault('request_published')
        deadline = time.monotonic() + timeout + 5
        while time.monotonic() < deadline:
            store.guard(credentials, actor)
            receipt = client.status()
            if receipt is not None:
                current = store.inspect()['state']['workspaces'][assignment['workspace_id']]['state']
                if receipt['state'] == 'running' and current == 'launching':
                    marker.update(state='running', pid=receipt['pid'])
                    store.workspace_phase(credentials, actor, current, 'running', run=marker)
                if receipt['state'] in TERMINAL:
                    terminal = 'finished' if receipt['state'] == 'finished' else 'stopped'
                    marker.update(state=terminal, pid=receipt.get('pid'), exit_code=receipt.get('exit_code'),
                                  launcher_receipt=receipt)
                    store.workspace_phase(credentials, actor, current, terminal, run=marker)
                    if terminal != 'finished' or receipt['exit_code'] != 0:
                        raise ValueError('external worker failed/stopped; inspect launcher receipt')
                    return marker
                if receipt['state'] == 'unknown': raise ValueError('launcher execution outcome unknown')
            time.sleep(0.05)
        raise ValueError('external launcher receipt timeout')
    except BaseException:
        # Sending cancel is not proof that a sibling process stopped. Only a
        # validated terminal launcher receipt permits releasing that uncertainty.
        try:
            client.cancel()
            until = time.monotonic() + 3
            while time.monotonic() < until:
                receipt = client.status()
                if receipt is not None and receipt['state'] in TERMINAL: break
                time.sleep(0.05)
            current = store.inspect()['state']['workspaces'][assignment['workspace_id']]['state']
            if current in ('launching', 'running'):
                known = receipt is not None and receipt['state'] in TERMINAL
                target = 'stopped' if known else 'unknown'
                marker.update(state=target, launcher_receipt=receipt)
                if known: marker.update(pid=receipt.get('pid'), exit_code=receipt.get('exit_code'))
                store.workspace_phase(credentials, actor, current, target, run=marker, allow_fenced=True)
        except BaseException:
            pass  # Preserve launching/running; never turn missing evidence into stopped.
        raise
