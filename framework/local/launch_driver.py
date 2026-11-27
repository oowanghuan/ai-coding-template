"""Finite trusted launcher; deploy only an independently reviewed, hash-pinned copy.

Standalone stdlib module: never imports the candidate framework. Its protected
configuration defines all executable, environment, filesystem and job choices.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import time
import uuid
from datetime import datetime, timezone

ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')
SHA = re.compile(r'[0-9a-f]{64}\Z')
LIMIT = 262144
TERMINAL = {'finished', 'stopped', 'rejected', 'unknown'}


def utc():
    return datetime.now(timezone.utc).isoformat()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def strict_json(data):
    def pairs(rows):
        value = {}
        for k, v in rows:
            if k in value:
                raise ValueError('duplicate JSON key')
            value[k] = v
        return value
    def constant(value):
        raise ValueError('non-finite JSON number')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def keys(value, required):
    if type(value) is not dict or set(value) != set(required.split()):
        raise ValueError('unexpected or missing fields')


def integer(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError('integer outside bound')


def no_links(path, directory=False):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute canonical path required')
    for item in list(reversed(path.parents)) + [path]:
        info = item.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise ValueError('symlink path refused')
    info = path.stat()
    if directory and not stat.S_ISDIR(info.st_mode):
        raise ValueError('directory required')
    if not directory and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
        raise ValueError('single-link regular file required')
    return path


def beneath(path, root):
    return Path(path) != Path(root) and Path(root) in Path(path).parents


def read_file(path, limit=LIMIT):
    path = no_links(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError('unsafe or oversized file')
        data = os.read(fd, limit + 1)
        if len(data) > limit:
            raise ValueError('oversized file')
        return data
    finally:
        os.close(fd)


def atomic(path, value):
    path = Path(path)
    no_links(path.parent, directory=True)
    if path.exists() or path.is_symlink():
        no_links(path)
    temporary = path.with_name('.write-' + uuid.uuid4().hex)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def validate_config(config):
    keys(config, 'format batch_id trusted_root candidate_root driver_sha256 python worker_program worker_sha256 request_dir receipt_dir scratch_root deadline_seconds jobs')
    if config['format'] != 'v4-launch-config/1' or not ID.fullmatch(config['batch_id']):
        raise ValueError('unsupported config or batch identity')
    for field in ('driver_sha256', 'worker_sha256'):
        if type(config[field]) is not str or not SHA.fullmatch(config[field]):
            raise ValueError('invalid program hash')
    if config['python'] != '/usr/bin/python3':
        raise ValueError('fixed system Python required')
    integer(config['deadline_seconds'], 1, 300)
    trusted = no_links(config['trusted_root'], directory=True)
    candidate = no_links(config['candidate_root'], directory=True)
    request = no_links(config['request_dir'], directory=True)
    receipt = no_links(config['receipt_dir'], directory=True)
    scratch = no_links(config['scratch_root'], directory=True)
    worker = no_links(config['worker_program'])
    if any(not beneath(p, trusted) for p in (receipt, scratch, worker)):
        raise ValueError('runtime authority must be beneath protected root')
    if any(a == b or beneath(a, b) or beneath(b, a) for a, b in ((receipt, scratch), (request, trusted))):
        raise ValueError('overlapping trust directories')
    if candidate == trusted or beneath(candidate, trusted) or beneath(trusted, candidate) or not beneath(request, candidate):
        raise ValueError('candidate anchor must separate protected root and contain mailbox')
    if beneath(worker, scratch) or beneath(worker, receipt):
        raise ValueError('program must not be in writable runtime directories')
    if hashlib.sha256(read_file(worker)).hexdigest() != config['worker_sha256']:
        raise ValueError('fixed Worker hash mismatch')
    if type(config['jobs']) is not list or not 1 <= len(config['jobs']) <= 2:
        raise ValueError('finite batch requires one or two jobs')
    seen_ids, seen_workspaces, seen_ops = set(), set(), set()
    for job in config['jobs']:
        keys(job, 'job_id operation_id workspace output content_sha256 max_delay_seconds max_runtime_seconds')
        if type(job['job_id']) is not str or not ID.fullmatch(job['job_id']):
            raise ValueError('invalid job identity')
        if type(job['operation_id']) is not str or not 1 <= len(job['operation_id']) <= 128:
            raise ValueError('invalid operation identity')
        workspace = no_links(job['workspace'], directory=True)
        if not beneath(workspace, candidate):
            raise ValueError('workspace outside candidate anchor')
        if workspace == trusted or beneath(workspace, trusted) or beneath(trusted, workspace):
            raise ValueError('workspace overlaps protected root')
        if workspace == request or beneath(request, workspace) or beneath(workspace, request):
            raise ValueError('workspace overlaps request mailbox')
        relative = job['output']
        if type(relative) is not str or not relative or relative.startswith('/') or any(
                part in ('', '.', '..', '.git', '.ai-org') for part in relative.split('/')):
            raise ValueError('unsafe fixed output')
        no_links((workspace / relative).parent, directory=True)
        target = workspace / relative
        if target.exists() or target.is_symlink():
            no_links(target)
        if type(job['content_sha256']) is not str or not SHA.fullmatch(job['content_sha256']):
            raise ValueError('invalid fixed content hash')
        integer(job['max_delay_seconds'], 0, 30); integer(job['max_runtime_seconds'], 1, 60)
        overlapping = any(workspace == Path(p) or beneath(workspace, p) or beneath(p, workspace)
                          for p in seen_workspaces)
        if job['job_id'] in seen_ids or overlapping or job['operation_id'] in seen_ops:
            raise ValueError('duplicate job/workspace/operation')
        seen_ids.add(job['job_id']); seen_workspaces.add(str(workspace)); seen_ops.add(job['operation_id'])
    return config


def validate_request(value, job):
    keys(value, 'format job_id operation_id content delay_seconds timeout')
    if value['format'] != 'v4-launch-request/1' or any(value[k] != job[k] for k in ('job_id', 'operation_id')):
        raise ValueError('request identity mismatch')
    if type(value['content']) is not str or len(value['content'].encode()) > 65536:
        raise ValueError('bounded content required')
    if hashlib.sha256(value['content'].encode()).hexdigest() != job['content_sha256']:
        raise ValueError('fixed content mismatch')
    integer(value['delay_seconds'], 0, job['max_delay_seconds'])
    integer(value['timeout'], 1, job['max_runtime_seconds'])
    return canonical_sha(value)


def policy(job, program, scratch, candidate_root):
    quote = lambda p: json.dumps(str(p))
    runtime = ['/System', '/usr', '/bin', '/Library/Developer', '/Library/Apple',
               '/private/preboot/Cryptexes', '/private/var/db/dyld']
    return '\n'.join([
        '(version 1)', '(deny default)', '(allow process*)', '(allow sysctl-read)',
        '(allow file-read-metadata)', '(allow file-map-executable)',
        '(allow mach-lookup (global-name "com.apple.system.logger"))',
        '(allow file-read* (literal "/") (literal "/dev/null") (literal "/dev/urandom") ' +
        ' '.join('(subpath ' + quote(p) + ')' for p in runtime + [str(scratch)]) +
        ' (literal ' + quote(program) + '))',
        '(allow file-write* (literal "/dev/null") (require-all (subpath ' + quote(candidate_root) +
        ') (literal ' + quote(Path(job['workspace']) / job['output']) +
        ')) (subpath ' + quote(scratch) + '))',
    ])


class Driver:
    def __init__(self, config, popen=subprocess.Popen, killpg=os.killpg,
                 clock=time.monotonic, sleep=time.sleep, config_sha256=None):
        self.config = validate_config(config)
        # The CLI supplies the actual config file byte hash. In-memory unit fixtures
        # use canonical bytes; they are not production execution evidence.
        self.config_sha256 = config_sha256 or canonical_sha(config)
        if not SHA.fullmatch(self.config_sha256):
            raise ValueError('invalid config fingerprint')
        self.popen, self.killpg, self.clock, self.sleep = popen, killpg, clock, sleep
        self.jobs = {j['job_id']: j for j in config['jobs']}
        self.records, self.owned, self.streams, self.deadlines, self.pending_input = {}, {}, {}, {}, {}
        # The outer policy must explicitly deny unlink/rename/replacement of C
        # itself, verified by real canaries; a non-writable parent alone is not
        # sufficient on Seatbelt. Walk below that anchor using directory FDs.
        fd = os.open(config['candidate_root'], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for part in Path(config['request_dir']).relative_to(config['candidate_root']).parts:
                following = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd); fd = following
            self.request_fd = fd
        except BaseException:
            os.close(fd)
            raise

    def mailbox(self, name):
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=self.request_fd)
        except FileNotFoundError:
            return None
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > LIMIT:
                raise ValueError('unsafe request mailbox entry')
            data = os.read(fd, LIMIT + 1)
            if len(data) > LIMIT:
                raise ValueError('oversized mailbox entry')
            return strict_json(data)
        finally:
            os.close(fd)

    def save(self, job_id, state, **fields):
        prior = self.records.get(job_id, {})
        record = dict(format='v4-launch-receipt/1', batch_id=self.config['batch_id'], job_id=job_id,
                      config_sha256=self.config_sha256,
                      operation_id=self.jobs[job_id]['operation_id'], request_sha256=None,
                      sequence=0, state=state, pid=None, exit_code=None, started_at=None,
                      finished_at=None, stdout_sha256=None, stderr_sha256=None)
        record.update(prior); record.update(fields); record['state'] = state
        record['sequence'] = prior.get('sequence', 0) + 1
        atomic(Path(self.config['receipt_dir']) / (job_id + '.json'), record)
        self.records[job_id] = record

    def restore(self):
        for job_id, job in self.jobs.items():
            path = Path(self.config['receipt_dir']) / (job_id + '.json')
            if path.exists() or path.is_symlink():
                record = strict_json(read_file(path))
                if any(record.get(k) != v for k, v in {'format': 'v4-launch-receipt/1',
                        'batch_id': self.config['batch_id'], 'job_id': job_id,
                        'config_sha256': self.config_sha256,
                        'operation_id': job['operation_id']}.items()):
                    raise ValueError('existing receipt identity mismatch')
                integer(record['sequence'], 1, 2**63 - 1)
                if record['state'] not in TERMINAL | {'launching', 'running'}:
                    raise ValueError('unknown receipt state')
                self.records[job_id] = record
                if record['state'] in ('launching', 'running'):
                    self.save(job_id, 'unknown', error='previous launch outcome requires external reconciliation')
            elif (Path(self.config['scratch_root']) / job_id).exists():
                self.save(job_id, 'unknown', error='runtime directory without receipt; preserve, do not launch')

    def launch(self, job_id, request):
        job = self.jobs[job_id]
        request_sha = validate_request(request, job)
        # All selected paths/program bytes are checked again immediately before launch.
        validate_config(self.config)
        scratch = Path(self.config['scratch_root']) / job_id
        self.save(job_id, 'launching', request_sha256=request_sha)
        scratch.mkdir(mode=0o700, exist_ok=False)
        script = scratch / 'policy.sb'
        script.write_text(policy(job, self.config['worker_program'], scratch, self.config['candidate_root']))
        streams = [(scratch / name).open('xb') for name in ('stdout.log', 'stderr.log')]
        self.streams[job_id] = streams
        env = {'HOME': str(scratch), 'TMPDIR': str(scratch), 'PATH': '/usr/bin:/bin',
               'PYTHONNOUSERSITE': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'LANG': 'en_US.UTF-8'}
        process = self.popen(['/usr/bin/sandbox-exec', '-f', str(script), self.config['python'],
                              '-I', '-B', '-S', self.config['worker_program']],
                             cwd=job['workspace'], env=env, stdin=subprocess.PIPE,
                             stdout=streams[0], stderr=streams[1], start_new_session=True)
        self.owned[job_id] = process  # Only this live object may authorize a signal.
        self.deadlines[job_id] = self.clock() + request['timeout']
        self.save(job_id, 'running', pid=process.pid, started_at=utc())
        os.set_blocking(process.stdin.fileno(), False)
        self.pending_input[job_id] = json.dumps({'path': job['output'], 'content': request['content'],
                                               'delay_seconds': request['delay_seconds']}).encode()

    def feed(self, job_id):
        if job_id not in self.pending_input:
            return
        process = self.owned[job_id]
        remaining = self.pending_input[job_id]
        try:
            sent = os.write(process.stdin.fileno(), remaining[:4096])
        except BlockingIOError:
            return  # The next tick still checks cancellation and the real deadline.
        remaining = remaining[sent:]
        if remaining:
            self.pending_input[job_id] = remaining
        else:
            del self.pending_input[job_id]
            process.stdin.close()

    def finish(self, job_id, state, error=None):
        process = self.owned[job_id]
        code = process.poll()
        if type(code) is not int:
            raise ValueError('exit has not been observed')
        process.stdin.close()
        self.pending_input.pop(job_id, None)
        for stream in self.streams.pop(job_id, []):
            stream.close()
        scratch = Path(self.config['scratch_root']) / job_id
        fields = dict(pid=process.pid, exit_code=code, finished_at=utc())
        try:
            fields.update({name + '_sha256': hashlib.sha256(read_file(scratch / (name + '.log'), 1048576)).hexdigest()
                           for name in ('stdout', 'stderr')})
        except (OSError, ValueError):
            state = 'unknown'; error = 'exited but log integrity unavailable'
        if error:
            fields['error'] = error
        self.save(job_id, state, **fields)
        del self.owned[job_id]

    def stop(self, job_id, reason):
        process = self.owned[job_id]
        try:
            if process.poll() is None:
                self.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=2)
            self.finish(job_id, 'stopped', reason)
        except (OSError, subprocess.TimeoutExpired):
            self.save(job_id, 'unknown', error='stop not confirmed: ' + reason)

    def tick(self):
        for job_id, job in self.jobs.items():
            record = self.records.get(job_id)
            if record and record['state'] in TERMINAL:
                continue
            request = None
            try:
                if job_id not in self.owned:
                    request = self.mailbox(job_id + '.request.json')
                    if request is None:
                        continue
                    request_sha = validate_request(request, job)
                    cancel = self.mailbox(job_id + '.cancel.json')
                    if cancel is not None:
                        keys(cancel, 'format job_id request_sha256')
                        if cancel != {'format': 'v4-launch-cancel/1', 'job_id': job_id,
                                      'request_sha256': request_sha}:
                            raise ValueError('cancel identity mismatch')
                        self.save(job_id, 'rejected', request_sha256=request_sha,
                                  error='cancelled before launch', finished_at=utc())
                        continue
                    self.launch(job_id, request)
                cancel = self.mailbox(job_id + '.cancel.json')
                if cancel is not None:
                    keys(cancel, 'format job_id request_sha256')
                    if cancel != {'format': 'v4-launch-cancel/1', 'job_id': job_id,
                                  'request_sha256': self.records[job_id]['request_sha256']}:
                        raise ValueError('cancel identity mismatch')
                    self.stop(job_id, 'cancel requested')
                elif self.owned[job_id].poll() is not None:
                    self.finish(job_id, 'finished')
                elif self.clock() >= self.deadlines[job_id]:
                    self.stop(job_id, 'runtime timeout')
                elif any((Path(self.config['scratch_root']) / job_id / n).stat().st_size > 1048576
                         for n in ('stdout.log', 'stderr.log')):
                    self.stop(job_id, 'log size bound')
                else:
                    self.feed(job_id)
            except Exception as error:
                if job_id in self.owned:
                    self.stop(job_id, 'launch/protocol error: ' + str(error)[:160])
                elif self.records.get(job_id, {}).get('state') == 'launching':
                    self.save(job_id, 'unknown', error='launch outcome unresolved: ' + str(error)[:160])
                else:
                    request_sha = canonical_sha(request) if type(request) is dict else None
                    self.save(job_id, 'rejected', request_sha256=request_sha,
                              error=str(error)[:160], finished_at=utc())

    def run(self):
        lock_path = Path(self.config['trusted_root']) / 'driver.lock'
        if lock_path.exists() or lock_path.is_symlink():
            no_links(lock_path)
        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.restore()
            deadline = self.clock() + self.config['deadline_seconds']
            while self.clock() < deadline:
                self.tick()
                if all(self.records.get(j, {}).get('state') in TERMINAL for j in self.jobs):
                    return
                self.sleep(0.05)
            for job_id in list(self.owned):
                self.stop(job_id, 'batch deadline')
        finally:
            # Only children owned by this driver incarnation; never persisted PIDs.
            for job_id in list(self.owned):
                self.stop(job_id, 'driver shutdown')
            for streams in self.streams.values():
                for stream in streams:
                    stream.close()
            os.close(self.request_fd); os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config_bytes = read_file(args.config)
    config = validate_config(strict_json(config_bytes))
    trusted = Path(config['trusted_root'])
    program = no_links(Path(__file__).absolute())
    if not beneath(args.config, trusted) or not beneath(program, trusted):
        raise ValueError('config and driver must be in protected root')
    if hashlib.sha256(read_file(program)).hexdigest() != config['driver_sha256']:
        raise ValueError('driver hash mismatch')
    Driver(config, config_sha256=hashlib.sha256(config_bytes).hexdigest()).run()


if __name__ == '__main__':
    main()
