"""Owned local process transport, wired only by a reviewed controller.

No provider branches, authentication, sandbox changes or implicit environment.
This module is NOT a sandbox: deploy a reviewed pinned copy in a protected
supervisor, with the existing approved CLI execution boundary. Candidate work
must not write its journal/config. Tests alone do not establish that deployment.
"""
import copy
import fcntl
import hashlib
import os
from pathlib import Path
import selectors
import stat
import subprocess
import threading
import time

from framework.local.launch_driver import atomic, canonical_sha, no_links, read_file, DIRECT_WORKSPACE_PREFIX
from .runspec import ID, bounded_run_request

TERMINAL = {'exited', 'stopped', 'timed_out', 'output_limited', 'outcome_unknown'}


def _stop_unknown(record, proc, reason):
    """Best effort on the owned handle only; never assert all writers stopped."""
    if proc is not None:
        try:
            if proc.poll() is None: proc.kill()
            proc.wait(timeout=5)
        except Exception: pass  # Preserve uncertainty if OS stop/wait fails.
    record.update(state='outcome_unknown', exit_code=None if proc is None else proc.returncode,
                  reason=reason)


def _close_resources(*resources):
    # One failed close must not prevent closing other handles or clearing _live.
    for resource in resources:
        if resource is not None:
            try: resource.close()
            except Exception: pass


class AuthorityWatch:
    """Read-only checks off the supervision thread; a stuck check loses freshness.

    This observes authorization, not kernel write permission. Only the owned
    process is stopped; descendant isolation/stop proof remains separate.
    """
    INTERVAL = 0.25
    MAX_STALE = 2.0

    def __init__(self, check, record):
        self.check = check; self.record = copy.deepcopy(record)
        self.closed = threading.Event(); self.lock = threading.Lock()
        self.last_valid = time.monotonic(); self.failure = None; self.checks = 0
        self.last_result = 'pending'
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while not self.closed.is_set():
            try:
                result = self.check(copy.deepcopy(self.record)) is True
                failure = None if result else 'authority_revoked'
            except Exception:
                result = False; failure = 'authority_check_error'
            with self.lock:
                self.checks += 1
                self.last_result = 'valid' if result else 'unavailable'
                if time.monotonic() - self.last_valid >= self.MAX_STALE:
                    self.failure = 'authority_check_timeout'
                elif result: self.last_valid = time.monotonic()
                else: self.failure = failure
                failed = self.failure is not None
            if failed or self.closed.wait(self.INTERVAL): return

    def snapshot(self):
        with self.lock:
            # Once a deadline is exceeded, a late successful response cannot
            # revive the original process or authorize a replacement launch.
            if self.failure is None and time.monotonic() - self.last_valid >= self.MAX_STALE:
                self.failure = 'authority_check_timeout'
            return dict(supported=True, checks=self.checks, last_result=self.last_result,
                        failure=self.failure, interval_seconds=self.INTERVAL, max_stale_seconds=self.MAX_STALE)


class LaunchReservations:
    """Shared protected launch fence, not a task/permission authority.

    Trusted application wiring MUST bind every executor/controller for one pool
    to the same persistent root. Never create a root per provider or retry.
    Reservations are irreversible here: reconciliation cannot silently rearm a
    workspace, even after an observed process exit. A lost write receipt fails
    closed. The authoritative Store still grants and fences Assignments.
    """
    def __init__(self, root):
        self.root = no_links(root, directory=True)

    def reserve(self, record, *, cwd, journal_root):
        from .results import strict_json
        lock = self.root / 'launch.lock'
        if lock.exists() or lock.is_symlink(): no_links(lock)
        with lock.open('a+') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            path = self.root / 'launches.json'
            value = strict_json(read_file(path)) if path.exists() or path.is_symlink() else {
                'format': 'launch-reservations/1', 'intents': []}
            if set(value) != {'format', 'intents'} or value['format'] != 'launch-reservations/1' or type(value['intents']) is not list:
                raise ValueError('invalid launch reservation journal')
            for prior in value['intents']:
                previous = Path(prior['cwd'])
                if (prior['authority']['assignment_id'] == record['authority']['assignment_id'] or
                        prior['authority']['workspace_id'] == record['authority']['workspace_id'] or
                        previous == cwd or previous in cwd.parents or cwd in previous.parents):
                    raise ValueError('execution authority/workspace already bound across adapters; reconcile original invocation')
            value['intents'].append(dict(authority=copy.deepcopy(record['authority']), cwd=str(cwd),
                journal_root=str(journal_root), invocation_id=record['invocation_id'],
                binding_sha256=record['binding_sha256'], intent_sha256=record['intent_sha256'],
                selection=copy.deepcopy(record['selection']), state='launch_reserved'))
            atomic(path, value)  # No replay returns a fresh permission to spawn.


class ProcessExecutor:
    """One trusted binding; no caller-supplied executable, cwd or environment.

    authorize must recheck current Assignment, lease, scope, budget and Worker
    eligibility. Selection is metadata, not authorization. Stop observes only
    the owned process: callers still need existing writer-stop/handoff proofs.
    """
    def __init__(self, *, selection, argv, cwd, environment, journal_root,
                 pinned_files, authorize, launch_reservations):
        if not isinstance(launch_reservations, LaunchReservations):
            raise ValueError('shared protected launch reservations required')
        if not callable(authorize): raise ValueError('live authorization checker required')
        if not isinstance(argv, (list, tuple)) or not argv or any(type(x) is not str or '\0' in x for x in argv):
            raise ValueError('fixed argv required')
        if not isinstance(environment, dict) or any(type(k) is not str or type(v) is not str for k, v in environment.items()):
            raise ValueError('explicit environment required; no implicit inheritance')
        self.root = no_links(journal_root, directory=True)
        self.cwd = no_links(cwd, directory=True)
        self.reservations = launch_reservations
        self.launch_domain = str(launch_reservations.root)
        if (self.reservations.root == self.cwd or self.reservations.root in self.cwd.parents or
                self.cwd in self.reservations.root.parents):
            raise ValueError('protected launch reservations and work directory must be separate')
        if self.root == self.cwd or self.root in self.cwd.parents or self.cwd in self.root.parents:
            raise ValueError('protected journal and work directory must be separate')
        if not isinstance(pinned_files, dict) or argv[0] not in pinned_files:
            raise ValueError('executable pin required')
        self.argv = tuple(argv); self.environment = dict(environment)
        self.pins = dict(pinned_files); self.selection = copy.deepcopy(selection)
        self.authorize = authorize; self._live = {}; self._mutex = threading.RLock()
        self.runtime_guard = getattr(launch_reservations, 'runtime_authorize', None)
        self.terminal_observer = getattr(launch_reservations, 'observe_terminal', None)
        if (self.runtime_guard is None) != (self.terminal_observer is None):
            raise ValueError('runtime authority and terminal observation must be bound together')
        if self.runtime_guard is not None and not all(callable(x) for x in (self.runtime_guard, self.terminal_observer)):
            raise ValueError('trusted runtime callbacks required')
        self._check_namespace()
        self._verify_pins()
        self.binding = canonical_sha(dict(argv=self.argv, cwd=str(self.cwd),
            environment=self.environment, pins=self.pins, selection=self.selection,
            launch_domain=self.launch_domain))

    def _check_namespace(self):
        # Preserve the previously reviewed never-launched recovery boundary.
        if (any(part.casefold().startswith(DIRECT_WORKSPACE_PREFIX)
                for path in (self.root, self.cwd, self.reservations.root) for part in path.parts) or
                any(DIRECT_WORKSPACE_PREFIX in arg.casefold() for arg in self.argv)):
            raise ValueError('external invocation cannot authorize direct-local-only namespace')

    def _verify_pins(self):
        for name, expected in self.pins.items():
            path = Path(name)
            no_links(path.parent, directory=True)
            if not stat.S_ISREG(path.lstat().st_mode):
                raise ValueError('pinned program/config must be a regular non-symlink file')
            # OS executables can have legitimate hardlinks. Their immutable
            # deployment and exact content pins are the boundary; journal files
            # still use the stricter single-link reader/writer.
            # Executables can exceed the small journal reader's size limit.
            with path.open('rb') as stream:
                digest = hashlib.sha256()
                for data in iter(lambda: stream.read(1048576), b''): digest.update(data)
            if digest.hexdigest() != expected: raise ValueError('execution input pin changed')

    def _lock(self):
        class Lock:
            def __enter__(inner):
                self._mutex.acquire()
                try:
                    path = self.root / 'invocation.lock'
                    if path.exists() or path.is_symlink(): no_links(path)
                    inner.file = path.open('a+')
                    fcntl.flock(inner.file, fcntl.LOCK_EX)
                except BaseException:
                    self._mutex.release(); raise
            def __exit__(inner, *args):
                inner.file.close(); self._mutex.release()
        return Lock()

    def _path(self, invocation_id):
        if not isinstance(invocation_id, str) or not ID.fullmatch(invocation_id):
            raise ValueError('invalid invocation ID')
        return self.root / (invocation_id + '.json')

    def _read(self, invocation_id):
        from .results import strict_json
        record = strict_json(read_file(self._path(invocation_id)))
        if record['binding_sha256'] != self.binding or record['selection'] != self.selection:
            raise ValueError('invocation belongs to another binding')
        return record

    def _view(self, record):
        value = copy.deepcopy(record)
        if record['state'] not in TERMINAL and record['invocation_id'] not in self._live:
            value.update(last_recorded_state=record['state'], state='outcome_unknown')
        return value

    def start(self, *, operation_id, authority, proposal):
        if not isinstance(operation_id, str) or not ID.fullmatch(operation_id): raise ValueError('operation ID')
        if (type(authority) is not dict or set(authority) != {'assignment_id', 'workspace_id', 'epoch', 'token'} or
                any(type(authority[k]) is not int or authority[k] < 1 for k in ('epoch', 'token')) or
                any(type(authority[k]) is not str or not ID.fullmatch(authority[k]) for k in ('assignment_id', 'workspace_id'))):
            raise ValueError('exact execution authority required')
        fields = bounded_run_request(**{k: proposal[k] for k in ('work_package_id', 'assignment_id', 'baseline_sha',
            'timeout_seconds', 'max_output_bytes', 'model')}, prompt=proposal['stdin'])
        if (proposal.get('execution_authorized') is not False or proposal.get('selection') != self.selection or
                proposal['assignment_id'] != authority['assignment_id']):
            raise ValueError('proposal/selection/authority mismatch')
        identity = 'inv-' + canonical_sha(dict(operation_id=operation_id, binding=self.binding))
        intent = canonical_sha(dict(binding=self.binding, request=fields, authority=authority))
        with self._lock():
            path = self._path(identity)
            if path.exists() or path.is_symlink():
                record = self._read(identity)
                if record['intent_sha256'] != intent: raise ValueError('operation reused for different intent')
                return self._view(record)
            for prior_path in self.root.glob('inv-*.json'):
                # A shared output directory may contain other bindings. Those
                # records are collision evidence, not this executor's status.
                from .results import strict_json
                prior = strict_json(read_file(prior_path))
                if (prior['authority'] == authority or
                        prior['authority']['workspace_id'] == authority['workspace_id']):
                    raise ValueError('execution authority/workspace already bound; reconcile original invocation')
            self._check_namespace()
            self._verify_pins()
            if self.authorize(copy.deepcopy(authority), copy.deepcopy(proposal)) is not True:
                raise ValueError('current execution authority not verified')
            record = dict(format='provider-invocation/1', invocation_id=identity,
                selection=self.selection, binding_sha256=self.binding, intent_sha256=intent,
                work_package_id=fields['work_package_id'], baseline_sha=fields['baseline_sha'],
                stdin_sha256=fields['stdin_sha256'], timeout_seconds=fields['timeout_seconds'],
                max_output_bytes=fields['max_output_bytes'],
                state='launch_intent', authority=copy.deepcopy(authority), exit_code=None,
                engineering_accepted=False, writer_stop_confirmed=False,
                evidence_level='untrusted_stdout', stdout_sha256=None, stderr_sha256=None)
            self.reservations.reserve(record, cwd=self.cwd, journal_root=self.root)
            atomic(path, record)  # Unknown response must never cause another launch.
            stdin = self.root / (identity + '.stdin')
            with stdin.open('xb') as stream: stream.write(fields['stdin'].encode())
            if self.authorize(copy.deepcopy(authority), copy.deepcopy(proposal)) is not True:
                record.update(state='outcome_unknown', reason='authority changed before launch')
                atomic(path, record); return self._view(record)
            self._verify_pins()
            no_links(self.cwd, directory=True)
            self._check_namespace()
            proc = None
            try:
                with stdin.open('rb') as stream:
                    proc = subprocess.Popen(self.argv, cwd=self.cwd, env=self.environment,
                        stdin=stream, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        close_fds=True, start_new_session=True)
            except Exception as error:
                _stop_unknown(record, proc, type(error).__name__)
                if proc is not None: _close_resources(proc.stdout, proc.stderr)
                atomic(path, record); return self._view(record)
            try:
                live = dict(process=proc, stop=threading.Event())
                self._live[identity] = live; record.update(state='running')
                # Protect construction as well as start after acquiring proc.
                # Start before a potentially slow/failing journal write. The
                # final supervisor write takes this same lock.
                thread = threading.Thread(target=self._supervise,
                    args=(copy.deepcopy(record), live, fields['timeout_seconds'], fields['max_output_bytes']), daemon=True)
                live['thread'] = thread
                thread.start()
            except Exception:
                _stop_unknown(record, proc, 'supervision thread initialization failed')
                _close_resources(proc.stdout, proc.stderr)
                self._live.pop(identity, None)
                atomic(path, record)
                raise
            atomic(path, record)
            return copy.deepcopy(record)

    def _supervise(self, record, live, seconds, limit):
        proc = live['process']; selector = None; watch = None
        try:
            selector = selectors.DefaultSelector()
            buffers = {'stdout': bytearray(), 'stderr': bytearray()}; reason = None
            deadline = time.monotonic() + seconds
            for name in buffers:
                pipe = getattr(proc, name); os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, name)
            if self.runtime_guard is not None:
                watch = AuthorityWatch(self.runtime_guard, record)
            while selector.get_map() or proc.poll() is None:
                if live['stop'].is_set(): reason = 'stopped'
                if watch is not None:
                    observed = watch.snapshot()
                    if observed['failure']:
                        record['stop_reason'] = observed['failure']; reason = reason or 'stopped'
                if time.monotonic() >= deadline: reason = reason or 'timed_out'
                if reason:
                    if proc.poll() is None: proc.kill()  # Only this owned handle.
                    break
                for key, _ in selector.select(timeout=0.05):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data: selector.unregister(key.fileobj); continue
                    remaining = limit - sum(len(v) for v in buffers.values())
                    buffers[key.data].extend(data[:remaining])
                    if len(data) > remaining: reason = 'output_limited'; break
            if reason is None:
                try: proc.wait(timeout=max(0.01, deadline - time.monotonic()))
                except subprocess.TimeoutExpired:
                    reason = 'timed_out'
                    if proc.poll() is None: proc.kill()
            proc.wait(timeout=5)
            record.update(state=reason or 'exited', exit_code=proc.returncode)
            record['authority_watch'] = watch.snapshot() if watch is not None else {'supported': False}
            for name, data in buffers.items():
                out = self.root / (record['invocation_id'] + '.' + name)
                with out.open('xb') as stream: stream.write(data); stream.flush(); os.fsync(stream.fileno())
                record[name + '_sha256'] = hashlib.sha256(data).hexdigest()
            with self._lock(): atomic(self._path(record['invocation_id']), record)
        except Exception as error:
            _stop_unknown(record, proc, 'supervision failed: ' + type(error).__name__)
            try:
                with self._lock(): atomic(self._path(record['invocation_id']), record)
            except Exception: pass  # Prior launch intent remains unknown on recovery.
        finally:
            if watch is not None: watch.closed.set()
            _close_resources(selector, proc.stdout, proc.stderr)
            with self._mutex: self._live.pop(record['invocation_id'], None)

    def status(self, *, invocation_id):
        with self._lock(): return self._view(self._read(invocation_id))

    def stop(self, *, invocation_id):
        with self._lock():
            record = self._read(invocation_id)
            if record['state'] not in TERMINAL and invocation_id in self._live:
                self._live[invocation_id]['stop'].set()
            return self._view(record)  # Request is not a stop receipt.

    def result(self, *, invocation_id):
        with self._lock():
            record = self._view(self._read(invocation_id))
            if record['state'] not in TERMINAL or record['stdout_sha256'] is None:
                raise ValueError('result unavailable; reconcile running or unknown invocation')
            for name in ('stdout', 'stderr'):
                data = read_file(self.root / (invocation_id + '.' + name), limit=1048576)
                if hashlib.sha256(data).hexdigest() != record[name + '_sha256']:
                    raise ValueError('result content changed')
                record[name] = data
        if self.terminal_observer is not None:
            # Store locking and idempotent write happen outside the invocation
            # lock. Failure can be reconciled by reading result again, never by
            # restarting the process. Raw provider output cannot choose actions.
            record['store_observation'] = self.terminal_observer(copy.deepcopy(record))
        return record

    def checkpoint(self, *, invocation_id, operation_id, completed=(), remaining=(), evidence_refs=()):
        from .preservation import preserve_invocation
        return preserve_invocation(self, invocation_id, operation_id=operation_id,
            completed=completed, remaining=remaining, evidence_refs=evidence_refs)
