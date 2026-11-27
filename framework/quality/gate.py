"""Read-only deterministic Gate for an operator-pinned, OS-protected local bundle.

The caller must obtain the trust-file hash independently of candidate reports.
Neither JSON validity nor this module can establish OS protection from a flag.
No test execution, task mutation, review signature or business acceptance occurs.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from datetime import datetime, timezone

from jsonschema import Draft202012Validator, validators
from referencing import Registry

SCHEMA = Path(__file__).resolve().parents[2] / 'schemas/evidence.schema.json'
JSON_LIMIT = 4 * 1024 * 1024
LOG_LIMIT = 1024 * 1024
SOURCE_LIMIT = 16 * 1024 * 1024
StrictValidator = validators.extend(Draft202012Validator, type_checker=
    Draft202012Validator.TYPE_CHECKER.redefine('integer', lambda checker, value: type(value) is int))
# Darwin O_SEARCH is defined in sys/fcntl.h but not exported by Python 3.9.
# It traverses ancestors without granting their directory-listing permission.
DIRECTORY_ACCESS = 0x40000000 if sys.platform == 'darwin' else getattr(os, 'O_PATH', os.O_RDONLY)


class InvalidBundle(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse(data):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise InvalidBundle('duplicate-json-key')
            result[key] = value
        return result
    def bad_constant(value):
        raise InvalidBundle('non-finite-json-number')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=bad_constant)


def path_checked(path, directory=False):
    path = Path(path)
    if not path.is_absolute() or path.resolve() != path:
        raise InvalidBundle('noncanonical-or-linked-path')
    info = path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise InvalidBundle('not-directory')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise InvalidBundle('not-single-link-regular-file')
    return path


def read_bytes(path, limit=JSON_LIMIT):
    path = path_checked(path)
    parent = os.open('/', DIRECTORY_ACCESS | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, DIRECTORY_ACCESS | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent); parent = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    finally:
        os.close(parent)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise InvalidBundle('unsafe-or-oversized-file')
        chunks = []; remaining = limit + 1
        while remaining:
            block = os.read(fd, min(65536, remaining))
            if not block:
                break
            chunks.append(block); remaining -= len(block)
        data = b''.join(chunks)
        if len(data) > limit:
            raise InvalidBundle('oversized-file')
        return data
    finally:
        os.close(fd)


def beneath(path, root):
    return Path(path) != Path(root) and Path(root) in Path(path).parents


def relative(value):
    if not isinstance(value, str) or not value or value.startswith('/') or any(
            part in ('', '.', '..', '.git') for part in value.split('/')) or '\x00' in value:
        raise InvalidBundle('unsafe-relative-path')
    return value


def timestamp(value):
    result = datetime.fromisoformat(value[:-1] + '+00:00' if value.endswith('Z') else value)
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise InvalidBundle('non-utc-time')
    return result.astimezone(timezone.utc)


def schema_errors(value, kind):
    schema = parse(read_bytes(SCHEMA))
    definition = {'$ref': '#/$defs/' + kind, '$defs': schema['$defs']}
    Draft202012Validator.check_schema(definition)
    validator = StrictValidator(definition, registry=Registry())
    # Bounded stable paths, rather than reflecting possibly private input values.
    return sorted(set('schema:' + kind + ':' + '/'.join(map(str, e.absolute_path))
                      for e in validator.iter_errors(value)))


def git_object(kind, data):
    return hashlib.sha1(kind.encode() + b' ' + str(len(data)).encode() + b'\0' + data).digest()


def snapshot_tree(subject_root, manifest):
    root = path_checked(subject_root, directory=True)
    observed = set()
    for parent, directories, files in os.walk(root, followlinks=False):
        for name in directories:
            path_checked(Path(parent) / name, directory=True)
        for name in files:
            observed.add(str((Path(parent) / name).relative_to(root)))
            if len(observed) > 1024:
                raise InvalidBundle('snapshot-file-limit')
    if observed != set(manifest):
        raise InvalidBundle('snapshot-file-set-mismatch')
    tree = {}; size = 0
    for name in sorted(manifest):
        relative(name)
        path = root / name
        data = read_bytes(path, SOURCE_LIMIT)
        size += len(data)
        if size > 64 * 1024 * 1024:
            raise InvalidBundle('snapshot-byte-limit')
        record = manifest[name]
        if digest(data) != record['sha256']:
            raise InvalidBundle('snapshot-content-mismatch')
        if bool(path.stat().st_mode & stat.S_IXUSR) != (record['mode'] == '100755'):
            raise InvalidBundle('snapshot-mode-mismatch')
        current = tree
        parts = name.split('/')
        for part in parts[:-1]:
            current = current.setdefault(part, {})
            if not isinstance(current, dict):
                raise InvalidBundle('snapshot-path-conflict')
        current[parts[-1]] = (record['mode'], git_object('blob', data))
    def build(directory):
        raw = bytearray()
        for name in sorted(directory, key=lambda n: (n + ('/' if isinstance(directory[n], dict) else '')).encode()):
            value = directory[name]
            mode, object_id = ('40000', build(value)) if isinstance(value, dict) else value
            raw.extend(mode.encode() + b' ' + name.encode() + b'\0' + object_id)
        return git_object('tree', bytes(raw))
    return build(tree).hex()


def verify_bundle(trust_path, expected_trust_sha256, run_id):
    """Verify a protected registered bundle. The trust pin is an operator input.

    All decisions are functions of the loaded bytes, explicit run identity and
    pin. No wall-clock value enters the result; identical inputs repeat exactly.
    """
    result = dict(format='quality-gate/1', status='unverifiable', reasons=[], gate_id=None,
                  evidence_id=None, evidence_sha256=None, plan_sha256=None,
                  trust_sha256=None, wp_id=None, wp_revision=None, subject=None)
    invalid, failed = set(), set()
    def finish():
        result['status'] = 'unverifiable' if invalid else ('failed' if failed else 'passed')
        result['reasons'] = sorted(invalid | failed)
        bound = dict(result); bound.pop('gate_id')
        result['gate_id'] = digest(canonical({'expected_trust_sha256': expected_trust_sha256,
                                             'requested_run_id': run_id, 'decision': bound}))
        return result
    stage = 'trust'
    try:
        if not isinstance(expected_trust_sha256, str) or len(expected_trust_sha256) != 64:
            invalid.add('trust:invalid-operator-pin'); return finish()
        trust_bytes = read_bytes(Path(trust_path))
        result['trust_sha256'] = digest(trust_bytes)
        if result['trust_sha256'] != expected_trust_sha256:
            invalid.add('trust:pin-mismatch'); return finish()
        trust = parse(trust_bytes)
        invalid.update(schema_errors(trust, 'trust'))
        if invalid:
            return finish()
        registration = trust['runs'].get(run_id)
        if registration is None:
            invalid.add('trust:unregistered-run'); return finish()
        root = path_checked(registration['root'], directory=True)
        result.update(evidence_id=run_id, wp_id=registration['wp_id'],
                      wp_revision=registration['wp_revision'], subject=registration['subject'])
        stage = 'plan'
        plan_bytes = read_bytes(root / 'plan.json')
        result['plan_sha256'] = digest(plan_bytes)
        if result['plan_sha256'] != registration['plan_sha256']:
            invalid.add('plan:registered-hash-mismatch'); return finish()
        plan = parse(plan_bytes)
        invalid.update(schema_errors(plan, 'plan'))
        if invalid:
            return finish()
        if (plan['run_id'] != run_id or plan['trusted_root'] != str(root)
                or any(plan[field] != registration[field] for field in
                       ('collector_sha256', 'wp_id', 'wp_revision', 'subject'))):
            invalid.add('plan:registration-binding-mismatch')
        scratch = path_checked(plan['scratch_root'], directory=True)
        subject_root = path_checked(plan['subject_root'], directory=True)
        if root == scratch or beneath(root, scratch) or beneath(scratch, root):
            invalid.add('plan:trust-scratch-overlap')
        if subject_root != root / 'subject':
            invalid.add('plan:subject-not-fixed-path')
        relative(plan['entrypoint'])
        if plan['entrypoint'] not in plan['manifest'] or not plan['entrypoint'].endswith('.py'):
            invalid.add('plan:entrypoint-not-in-manifest')
        tests = {case['id']: case for case in plan['tests']}
        if len(tests) != len(plan['tests']):
            invalid.add('plan:duplicate-check-id')
        if sum(case['timeout_seconds'] for case in plan['tests']) > 120:
            invalid.add('plan:aggregate-timeout-limit')
        if any(len(case['input'].encode()) > 65536 for case in plan['tests']):
            invalid.add('plan:input-byte-limit')
        if digest(canonical(plan['manifest'])) != plan['subject']['manifest_sha256']:
            invalid.add('plan:manifest-fingerprint-mismatch')
        commit_bytes = plan['commit_object'].encode()
        header = plan['commit_object'].split('\n\n', 1)[0].splitlines()
        if (git_object('commit', commit_bytes).hex() != plan['subject']['commit']
                or [line for line in header if line.startswith('tree ')] != ['tree ' + plan['subject']['tree']]):
            invalid.add('plan:commit-object-binding-mismatch')
        if invalid:
            return finish()
        if snapshot_tree(subject_root, plan['manifest']) != plan['subject']['tree']:
            invalid.add('plan:git-tree-mismatch'); return finish()
        stage = 'receipt'
        evidence_bytes = read_bytes(root / 'evidence.json')
        result['evidence_sha256'] = digest(evidence_bytes)
        evidence = parse(evidence_bytes)
        invalid.update(schema_errors(evidence, 'evidence'))
        if invalid:
            return finish()
        if (evidence['evidence_id'] != run_id or evidence['plan_sha256'] != result['plan_sha256']
                or any(evidence[field] != plan[field] for field in
                       ('collector_sha256', 'wp_id', 'wp_revision', 'kind', 'subject', 'environment'))):
            invalid.add('receipt:plan-binding-mismatch')
        if evidence['state'] != 'complete':
            invalid.add('receipt:unknown-outcome')
        if not evidence['source_unchanged']:
            invalid.add('receipt:source-changed')
        start, end = timestamp(evidence['started_at']), timestamp(evidence['finished_at'])
        if start > end:
            invalid.add('receipt:time-order')
        cases = {case['id']: case for case in evidence['cases']}
        if len(cases) != len(evidence['cases']) or set(cases) != set(tests):
            invalid.add('receipt:check-set-mismatch'); return finish()
        counts = {name: 0 for name in ('passed', 'failed', 'skipped', 'not_run')}
        executed = 0
        for identity in sorted(tests):
            stage = 'case:' + identity
            case, expected = cases[identity], tests[identity]
            counts[case['status']] += 1
            fixed_command = ['/usr/bin/python3', '-I', '-B', '-S', str(subject_root / plan['entrypoint'])]
            if (case['required'] != expected['required'] or case['expected_exit'] != expected['expected_exit']
                    or case['expected_stdout_sha256'] != expected['expected_stdout_sha256']
                    or case['input_sha256'] != digest(expected['input'].encode())
                    or case['command'] != fixed_command or case['cwd'] != str(scratch / identity)
                    or case['skip_reason'] != expected['skip_reason']):
                invalid.add(stage + ':plan-binding-mismatch')
            if case['output_limit_exceeded']:
                failed.add(stage + ':output-limit-exceeded')
            if case['collection_error'] is not None:
                invalid.add(stage + ':collection-error')
            if case['status'] in ('skipped', 'not_run'):
                if any(case[field] is not None for field in
                       ('pid', 'exit_code', 'signal', 'stdout', 'stderr', 'policy_sha256', 'started_at', 'finished_at')):
                    invalid.add(stage + ':nonexecuted-has-execution-fields')
                if case['timed_out'] or case['output_limit_exceeded']:
                    invalid.add(stage + ':nonexecuted-has-runtime-outcome')
                if case['status'] == 'not_run':
                    failed.add(stage + ':not-run')
                elif expected['required']:
                    failed.add(stage + ':required-skip')
                elif expected['skip_reason'] is None:
                    invalid.add(stage + ':unapproved-skip')
                continue
            executed += 1
            if expected['skip_reason'] is not None:
                invalid.add(stage + ':executed-approved-skip')
            if case['pid'] is None or case['started_at'] is None or case['finished_at'] is None:
                invalid.add(stage + ':missing-execution-identity')
            else:
                cstart, cend = timestamp(case['started_at']), timestamp(case['finished_at'])
                if not start <= cstart <= cend <= end:
                    invalid.add(stage + ':time-order')
            code = case['exit_code']
            if code is None and not case['timed_out'] and case['collection_error'] is None:
                invalid.add(stage + ':missing-observed-exit')
            if case['signal'] != (-code if code is not None and code < 0 else None):
                invalid.add(stage + ':signal-exit-mismatch')
            if case['policy_sha256'] is None:
                invalid.add(stage + ':missing-policy')
            elif digest(read_bytes(root / 'policies' / (identity + '.sb'))) != case['policy_sha256']:
                invalid.add(stage + ':policy-fingerprint-mismatch')
            logs = {}
            for channel in ('stdout', 'stderr'):
                descriptor = case[channel]
                if descriptor is None:
                    invalid.add(stage + ':missing-' + channel); continue
                filename = 'logs/' + identity + '.' + channel
                if descriptor['path'] != filename:
                    invalid.add(stage + ':unexpected-' + channel + '-path'); continue
                data = read_bytes(root / filename, LOG_LIMIT)
                if len(data) != descriptor['size'] or digest(data) != descriptor['sha256']:
                    invalid.add(stage + ':' + channel + '-fingerprint-mismatch')
                logs[channel] = data
            if len(logs) != 2:
                continue
            passed = (code == expected['expected_exit'] and case['signal'] is None
                      and not case['timed_out'] and not case['output_limit_exceeded']
                      and case['collection_error'] is None
                      and digest(logs['stdout']) == expected['expected_stdout_sha256'])
            observed = 'passed' if passed else 'failed'
            if case['status'] != observed:
                invalid.add(stage + ':reported-outcome-mismatch')
            if not passed:
                failed.add(stage + ':observed-check-failed')
        if counts != evidence['counts']:
            invalid.add('receipt:counts-mismatch')
        if not executed:
            failed.add('receipt:no-executed-checks')
        return finish()
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, RecursionError, OverflowError):
        invalid.add(stage + ':unreadable-or-invalid')
        return finish()
