"""Protected-input governance verifier. Callers must supply an out-of-band trust pin."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

from .core import (append_proposal, chain_errors, derive, evaluate_loaded, fingerprint,
                   impact, schema_errors, timestamp)

LIMIT = 4 * 1024 * 1024
# Darwin O_SEARCH: traverse directory descriptors without reading directory contents.
DIRECTORY_ACCESS = 0x40000000 if sys.platform == 'darwin' else getattr(os, 'O_PATH', os.O_RDONLY)


def read_bytes(path, limit=LIMIT):
    """Anchor every directory with no-follow fds; reject aliases and nonregular files."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute non-traversing path required')
    directory = os.open('/', DIRECTORY_ACCESS | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:-1]:
            next_fd = os.open(part, DIRECTORY_ACCESS | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory); directory = next_fd
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > limit:
                raise ValueError('bounded regular single-link input required')
            chunks = []; remaining = limit + 1
            while remaining:
                chunk = os.read(fd, min(65536, remaining))
                if not chunk: break
                chunks.append(chunk); remaining -= len(chunk)
            raw = b''.join(chunks); after = os.fstat(fd)
            if len(raw) > limit or (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError('input changed or exceeds bound')
            return raw
        finally: os.close(fd)
    finally: os.close(directory)


def decode(raw):
    def pairs(items):
        result = {}
        for key,value in items:
            if key in result: raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def invalid(_): raise ValueError('nonfinite JSON number')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=invalid)


def pinned(path, digest):
    raw = read_bytes(path)
    if hashlib.sha256(raw).hexdigest() != digest: raise ValueError('protected input fingerprint mismatch')
    return decode(raw)


def validate(value, kind):
    errors = schema_errors(value, kind)
    if errors: raise ValueError(';'.join(errors))
    return value


def directory(path):
    candidate = Path(path)
    if not candidate.is_absolute() or candidate != candidate.resolve(strict=True) or not candidate.is_dir():
        raise ValueError('canonical absolute directory required')
    return candidate


def inside(path, root):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts or path == root or root not in path.parents:
        raise ValueError('input outside protected boundary')
    return path


def load(trust_path, expected_trust_sha256, at):
    timestamp(at)
    trust = validate(pinned(trust_path, expected_trust_sha256), 'trust')
    trusted = directory(trust['trusted_root']); candidate = directory(trust['candidate_root'])
    if trusted == candidate or trusted in candidate.parents or candidate in trusted.parents:
        raise ValueError('trusted and candidate roots must be disjoint')
    inside(trust_path, trusted)
    ledger = validate(pinned(inside(trust['ledger']['path'], trusted), trust['ledger']['sha256']), 'ledger')
    if ledger['project_id'] != trust['project_id']: raise ValueError('ledger project mismatch')
    errors = chain_errors(ledger, trust['ledger'])
    if errors: raise ValueError(';'.join(errors))
    records = {}
    # Authenticate all registered sources, including pending append-proposal inputs.
    for source_id, binding in trust['sources'].items():
        records[source_id] = validate(pinned(inside(binding['path'], trusted), binding['sha256']), 'record')
    for entry in ledger['entries']:
        binding = trust['sources'].get(entry['source_id'])
        if binding is None or binding['sha256'] != entry['source_sha256']:
            raise ValueError('unregistered or mismatched history source')
    inside(trust['quality']['trust_path'], trusted)
    return trust, ledger, records


def quality_details(trust, run_id):
    # Import the real verifier, not a caller-provided passed JSON document.
    from framework.quality.gate import verify_bundle as verify_quality
    binding = trust['quality']; gate = verify_quality(binding['trust_path'], binding['trust_sha256'], run_id)
    result = {'gate':gate}
    if gate.get('status') not in ('passed','failed'): return result
    quality_trust = pinned(binding['trust_path'], binding['trust_sha256'])
    run = quality_trust['runs'][run_id]
    root = directory(run['root']); inside(root, Path(trust['trusted_root']))
    result['plan'] = pinned(root / 'plan.json', gate['plan_sha256'])
    result['evidence'] = pinned(root / 'evidence.json', gate['evidence_sha256'])
    return result


def finish(result, digest):
    result['trust_sha256'] = digest
    result['decision_id'] = fingerprint(result)
    return result


def verify_bundle(trust_path, expected_trust_sha256, signoff_id, candidate_path, at):
    """Evaluate only pinned inputs; effective does not establish current target validity."""
    try:
        trust, ledger, records = load(trust_path, expected_trust_sha256, at)
        candidate = validate(decode(read_bytes(inside(candidate_path, Path(trust['candidate_root'])))), 'candidate')
        state = derive(trust, ledger, records, at)
        signoff = state['signoffs'].get(signoff_id)
        review = state['reviews'].get(signoff['payload']['review_id']) if signoff else None
        quality = {'closures':{}, 'baselines':{}}; cache = {}
        def get(run_id):
            if run_id not in cache: cache[run_id] = quality_details(trust, run_id)
            return cache[run_id]
        if review:
            quality['review'] = get(review['payload']['quality_run_id'])
            for deviation_id in review['payload']['deviation_refs']:
                deviation = state['deviations'].get(deviation_id)
                if deviation:
                    if deviation['closure'] is not None:
                        quality['closures'][deviation_id] = get(deviation['closure']['quality_run_id'])
                    if deviation['baseline'] is not None:
                        quality['baselines'][deviation_id] = get(deviation['baseline']['quality_run_id'])
        if candidate['quality_run_id'] is not None: quality['candidate'] = get(candidate['quality_run_id'])
        result = evaluate_loaded(trust, ledger, records, signoff_id, candidate, at, quality)
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        result = {'format':'governance-decision/1','status':'unverifiable', 'signoff_id':signoff_id,
                  'reasons':['protected-verification:' + str(exc)]}
    # Include the limitation even when protected input loading fails. Hash it into
    # the decision so downstream consumers cannot omit it without changing the ID.
    result.update(verification_scope='locked_baseline', current_target_status='not_observed')
    return finish(result, expected_trust_sha256)


def inspect_bundle(trust_path, expected_trust_sha256, at, operation='inspect', changed=None, source_id=None):
    try:
        trust, ledger, records = load(trust_path, expected_trust_sha256, at)
        state = derive(trust, ledger, records, at)
        if state['errors']: raise ValueError(';'.join(state['errors']))
        if operation == 'impact': result = impact(state['registry'], changed or [])
        elif operation == 'export': result = {'status':'verified', 'ledger':ledger, 'records':records}
        elif operation == 'append-proposal':
            if source_id not in trust['sources']: raise ValueError('unregistered proposed source')
            result = append_proposal(ledger, source_id, trust['sources'][source_id]['sha256'])
            result['status'] = 'proposal'
        else: result = {'status':'verified','registry':state['registry'], 'revoked':state['revoked'],
                        'invalidated_signoffs':state['invalidated'], 'ledger_tip':trust['ledger']['head_sha256']}
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        result = {'status':'unverifiable','reasons':['protected-verification:' + str(exc)]}
    return finish(result, expected_trust_sha256)
