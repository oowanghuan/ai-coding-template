"""Pure governance history/impact evaluation; no authentication or task writes here."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import re

from jsonschema import Draft202012Validator, validators
from referencing import Registry

SCHEMA = Path(__file__).resolve().parents[2] / 'schemas/governance.schema.json'
ZERO = '0' * 64
StrictValidator = validators.extend(Draft202012Validator, type_checker=Draft202012Validator.TYPE_CHECKER.redefine('integer', lambda checker, value: type(value) is int))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def fingerprint(value): return hashlib.sha256(canonical(value)).hexdigest()


def timestamp(value): return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def schema_errors(value, kind):
    schema = json.loads(SCHEMA.read_text()); schema['oneOf'] = [{'$ref': '#/$defs/' + kind}]
    validator = StrictValidator(schema, registry=Registry())
    return sorted('schema:' + '/'.join(str(p) for p in error.absolute_path) + ':' + error.message
                  for error in validator.iter_errors(value))


def relative(path):
    if not isinstance(path, str) or not path or path.startswith('/') or '\\' in path:
        raise ValueError('unsafe governance path')
    if any(part in ('', '.', '..') for part in path.rstrip('/').split('/')):
        raise ValueError('unsafe governance path')
    return path


def within(path, scope): return path == scope or (scope.endswith('/') and path.startswith(scope))


def chain_errors(ledger, binding):
    errors = schema_errors(ledger, 'ledger')
    if errors: return errors
    previous = ZERO; seen = set()
    for number, entry in enumerate(ledger['entries'], 1):
        body = {key:value for key,value in entry.items() if key != 'entry_sha256'}
        if entry['sequence'] != number or entry['previous_sha256'] != previous:
            errors.append('history-chain-order')
        if entry['entry_sha256'] != fingerprint(body): errors.append('history-entry-fingerprint')
        if entry['source_id'] in seen: errors.append('history-source-reused')
        seen.add(entry['source_id']); previous = entry['entry_sha256']
    if len(ledger['entries']) != binding['sequence'] or previous != binding['head_sha256']:
        errors.append('protected-history-tip-mismatch')
    return sorted(set(errors))


def append_proposal(ledger, source_id, source_sha256):
    """Return an append-only proposal; only an external trusted operator can pin it."""
    if any(row['source_id'] == source_id for row in ledger['entries']): raise ValueError('history source already appended')
    entries = [dict(row) for row in ledger['entries']]
    entry = dict(sequence=len(entries)+1, source_id=source_id, source_sha256=source_sha256,
                 previous_sha256=entries[-1]['entry_sha256'] if entries else ZERO)
    entry['entry_sha256'] = fingerprint(entry); entries.append(entry)
    result = dict(ledger, entries=entries)
    return {'proposal': result, 'tip': {'sequence':len(entries), 'head_sha256':entry['entry_sha256']},
            'effective':False, 'reason':'operator must preserve history and pin the appended protected ledger'}


def impact(registry, changed):
    changed = set(changed)
    unknown = sorted(changed - set(registry))
    for item in registry.values(): unknown.extend(set(item['depends_on']) - set(registry))
    if unknown: return {'status':'unverifiable', 'affected':[], 'reasons':['unknown-contract:' + k for k in sorted(set(unknown))]}
    affected = set(changed)
    while True:
        more = {key for key,value in registry.items() if set(value['depends_on']) & affected}
        if more <= affected: break
        affected |= more
    return {'status':'known', 'affected':sorted(affected), 'reasons':[]}


def commit_errors(subject, body):
    data = body.encode('utf-8')
    errors = []
    if hashlib.sha1(b'commit ' + str(len(data)).encode() + b'\0' + data).hexdigest() != subject['commit']:
        errors.append('commit-object-sha-mismatch')
    header = body.split('\n\n', 1)[0].splitlines()
    trees = [line[5:] for line in header if line.startswith('tree ')]
    if trees != [subject['tree']]: errors.append('commit-object-tree-mismatch')
    return errors


def derive(trust, ledger, records, at):
    """Records here must have been authenticated by the protected-source loader."""
    result = {'registry':{}, 'reviews':{}, 'signoffs':{}, 'deviations':{}, 'invalidated':{}, 'invalidated_reviews':{}, 'revoked':{}, 'errors':[]}
    versions = {}; last_time = None
    for entry in ledger['entries']:
        source_id = entry['source_id']; record = records[source_id]; identity = trust['sources'][source_id]
        kind = record['kind']; payload = record['payload']; issued = timestamp(record['issued_at'])
        if issued > timestamp(at): result['errors'].append('record-in-future:' + source_id)
        if last_time is not None and issued < last_time: result['errors'].append('history-time-regression:' + source_id)
        last_time = issued
        role = identity['role']
        allowed = {'contract':('contract_owner','owner'), 'review':('reviewer',), 'signoff':('acceptor',),
                   'deviation':('owner',), 'revoke':('owner','acceptor')}
        if role not in allowed[kind]: result['errors'].append('source-role-not-authorized:' + source_id)
        if kind == 'contract':
            relative(payload['path']); key = payload['id']; old = result['registry'].get(key)
            version_key = (key, payload['version'])
            material = {k:payload[k] for k in ('path','sha256','depends_on')}
            if version_key in versions and versions[version_key] != material:
                result['errors'].append('immutable-contract-version-reused:' + key)
            versions[version_key] = material
            before = dict(result['registry']); result['registry'][key] = payload
            if old is not None and old != payload:
                # Union old/new reverse edges so deleting a dependency cannot hide prior impact.
                union = {k:dict(v) for k,v in result['registry'].items()}
                for node, data in before.items():
                    union[node] = dict(union[node], depends_on=sorted(set(union[node]['depends_on']) | set(data['depends_on'])))
                affected = impact(union, [key])
                for review_id, review in result['reviews'].items():
                    if affected['status'] != 'known' or set(affected['affected']) & {r['id'] for r in review['payload']['contract_refs']}:
                        result['invalidated_reviews'].setdefault(review_id, []).append('contract-change:' + key)
                for signoff_id, signoff in result['signoffs'].items():
                    review = result['reviews'].get(signoff['payload']['review_id'])
                    if review and (affected['status'] != 'known' or
                            set(affected['affected']) & {r['id'] for r in review['payload']['contract_refs']}):
                        result['invalidated'].setdefault(signoff_id, []).append('contract-change:' + key)
        elif kind == 'review':
            key = payload['id']
            if key in result['reviews']: result['errors'].append('review-id-reused:' + key)
            for path in payload['paths']: relative(path)
            result['reviews'][key] = {'payload':payload, 'identity':identity, 'source_id':source_id, 'sequence':entry['sequence']}
        elif kind == 'signoff':
            key = payload['id']
            if key in result['signoffs']: result['errors'].append('signoff-id-reused:' + key)
            review = result['reviews'].get(payload['review_id'])
            if review is None: result['errors'].append('signoff-before-review:' + key)
            else:
                if payload['review_id'] in result['invalidated_reviews']:
                    result['invalidated'].setdefault(key, []).append('review-invalidated-by-history')
                for ref in review['payload']['contract_refs']:
                    current = result['registry'].get(ref['id'])
                    if not current or any(current[k] != ref[k] for k in ('version','sha256')):
                        result['invalidated'].setdefault(key, []).append('contract-changed-before-signoff:' + ref['id'])
            result['signoffs'][key] = {'payload':payload, 'identity':identity, 'source_id':source_id, 'sequence':entry['sequence']}
        elif kind == 'revoke':
            key = payload['signoff_id']; signoff = result['signoffs'].get(key)
            if signoff is None: result['errors'].append('revoke-unknown-signoff:' + key)
            elif role != 'owner' and identity['principal'] != signoff['identity']['principal']:
                result['errors'].append('revoke-wrong-principal:' + key)
            result['revoked'][key] = payload['reason']
        elif kind == 'deviation':
            key = payload['id']; previous = result['deviations'].get(key)
            if payload['revision'] != (previous['revision'] + 1 if previous else 1):
                result['errors'].append('deviation-revision-gap:' + key)
            for path in payload['scope_paths']: relative(path)
            timestamp(payload['expires_at']); result['deviations'][key] = payload
    registry = result['registry']
    if not trust['graph_complete'] or set(registry) != set(trust['contracts']): result['errors'].append('impact-coverage-incomplete')
    for key, expected in trust['contracts'].items():
        if key in registry and set(registry[key]['depends_on']) != set(expected['depends_on']):
            result['errors'].append('impact-relation-missing-or-changed:' + key)
    if len({r['path'] for r in registry.values()}) != len(registry): result['errors'].append('conflicting-contract-authority-path')
    result['errors'] += impact(registry, [])['reasons']
    result['errors'] = sorted(set(result['errors']))
    return result


def dependencies(registry, required):
    affected = set(required)
    while True:
        more = {dep for key in affected if key in registry for dep in registry[key]['depends_on']}
        if more <= affected: return affected
        affected |= more


def mechanical_errors(policy, review_subject, candidate_subject, review_details, candidate_details):
    old = review_details.get('plan', {}).get('manifest')
    new = candidate_details.get('plan', {}).get('manifest')
    if not isinstance(old, dict) or not isinstance(new, dict): return ['mechanical-manifest-unverified']
    if fingerprint(old) != review_subject['manifest_sha256'] or fingerprint(new) != candidate_subject['manifest_sha256']:
        return ['mechanical-manifest-fingerprint-mismatch']
    actual = {path:{'old':old.get(path), 'new':new.get(path)} for path in set(old) | set(new) if old.get(path) != new.get(path)}
    if not actual: return ['different-tree-without-manifest-difference']
    if not policy: return ['mechanical-change-not-preauthorized']
    for path in policy: relative(path)
    if actual != policy: return ['mechanical-transform-outside-exact-policy']
    return []


def baseline_analysis(current, baseline, binding, wp_id):
    result = {'baseline_run_id':binding['quality_run_id'], 'status':'unverifiable', 'known_failures':[], 'new_failures':[]}
    gate = baseline.get('gate', {})
    if gate.get('status') not in ('passed','failed') or gate.get('subject') != binding['subject'] or gate.get('wp_id') != wp_id:
        return result
    if any(not isinstance(item.get('plan'),dict) or not isinstance(item.get('evidence'),dict) for item in (current,baseline)):
        return result
    def checks(details):
        plan = details['plan']; entry = plan['entrypoint']
        return {case['id']:fingerprint({'case':case, 'entrypoint':entry,
                    'entrypoint_file':plan['manifest'][entry], 'environment':details['evidence']['environment']}) for case in plan['tests']}
    def outcomes(details):
        return {case['id']:fingerprint({key:case.get(key) for key in ('exit_code','signal','timed_out')} |
                    {key:None if case.get(key) is None else {field:case[key].get(field) for field in ('sha256','size')}
                     for key in ('stdout','stderr')}) for case in details['evidence']['cases']}
    current_outcomes, old_outcomes = outcomes(current), outcomes(baseline)
    current_checks, old_checks = checks(current), checks(baseline)
    old_failures = {case['id'] for case in baseline['evidence']['cases'] if case['status']=='failed'}
    failures = {case['id'] for case in current['evidence']['cases'] if case['status']=='failed'}
    known = {case for case in failures if case in old_failures and case in current_checks and current_checks[case]==old_checks.get(case) and current_outcomes[case]==old_outcomes.get(case)}
    result.update(status='verified', known_failures=sorted(known), new_failures=sorted(failures-known))
    return result


def evaluate_loaded(trust, ledger, records, signoff_id, candidate, at, quality):
    """Locked-baseline decision; no live target ref is observed here.

    Injected quality details are synthetic tests, never CLI input.
    """
    derived = derive(trust, ledger, records, at); reasons = list(derived['errors']); unknown = bool(reasons)
    reviewed = quality.get('review', {}); gate = reviewed.get('gate', {})
    candidate_details = quality.get('candidate', {}); candidate_gate = candidate_details.get('gate', {})
    result = dict(format='governance-decision/1', status='unverifiable', reasons=[], signoff_id=signoff_id,
                  verification_scope='locked_baseline', current_target_status='not_observed',
                  review_id=None, wp_id=None, wp_revision=None, reviewed_subject=None,
                  candidate_subject=candidate['subject'], target_base_sha=candidate['target_base_sha'],
                  gate_id=gate.get('gate_id'), candidate_gate_id=candidate_gate.get('gate_id'), equivalence=None,
                  active_deviations=[], failure_analysis=[], invalidated_signoffs=sorted(derived['invalidated']),
                  ledger_tip=trust['ledger']['head_sha256'], trust_sha256=None)
    signoff = derived['signoffs'].get(signoff_id)
    if not signoff: reasons.append('unknown-signoff'); unknown = True
    review = derived['reviews'].get(signoff['payload']['review_id']) if signoff else None
    if not review: reasons.append('unknown-review'); unknown = True
    if review and signoff:
        payload = review['payload']; work = trust['work_packages'].get(payload['wp_id'])
        result.update(review_id=payload['id'], wp_id=payload['wp_id'], wp_revision=payload['wp_revision'], reviewed_subject=payload['subject'])
        if signoff_id in derived['revoked']: reasons.append('signoff-revoked')
        if signoff_id in derived['invalidated'] or payload['id'] in derived['invalidated_reviews']: reasons.append('signoff-invalidated-by-history')
        if payload['conclusion'] != 'approved' or not payload['summary'].strip(): reasons.append('review-not-approved')
        reasons += commit_errors(payload['subject'], payload['commit_object'])
        reasons += commit_errors(candidate['subject'], candidate['commit_object'])
        if candidate['wp_id'] != payload['wp_id'] or candidate['wp_revision'] != payload['wp_revision']: reasons.append('candidate-work-package-mismatch')
        same_tree = all(candidate['subject'][k] == payload['subject'][k] for k in ('tree','manifest_sha256'))
        result['equivalence'] = ('exact_object' if candidate['subject']['commit']==payload['subject']['commit'] else 'same_tree_commit') if same_tree else 'mechanical_manifest'
        if not work: reasons.append('unknown-work-package-policy'); unknown = True
        else:
            if work['revision'] != payload['wp_revision']: reasons.append('work-package-revision-mismatch')
            if payload['policy_sha256'] != fingerprint(work): reasons.append('review-policy-fingerprint-mismatch')
            if payload['target_base_sha'] != work['target_base_sha'] or candidate['target_base_sha'] != work['target_base_sha']:
                reasons.append('target-base-changed-recheck-required')
            if set(candidate['paths']) != set(payload['paths']): reasons.append('candidate-reviewed-paths-mismatch')
            for path in candidate['paths']: relative(path)
            if any(not any(within(relative(path), scope) for scope in payload['paths']) for path in work['required_paths']):
                reasons.append('review-required-paths-missing')
            needed = dependencies(derived['registry'], work['required_contracts'])
            if not needed <= {ref['id'] for ref in payload['contract_refs']}: reasons.append('required-contract-bindings-missing')
            if not needed <= set(derived['registry']): reasons.append('required-contract-unknown'); unknown = True
            if work['risk'] == 'high':
                for name, identity in [('reviewer',review['identity']),('acceptor',signoff['identity'])]:
                    if (identity['principal'] in work['author_principals'] or identity['context_id'] in work['author_contexts']
                            or identity['independence_group'] in work['author_groups']): reasons.append('high-risk-'+name+'-not-independent')
                if work['separate_acceptor'] and (review['identity']['principal'] == signoff['identity']['principal'] or
                        review['identity']['context_id'] == signoff['identity']['context_id']): reasons.append('acceptor-not-separated-from-reviewer')
            if same_tree and candidate['subject']['commit'] != payload['subject']['commit'] and not work['allow_same_tree_commit']:
                reasons.append('different-commit-not-preauthorized')
            if not same_tree:
                reasons += mechanical_errors(work['mechanical_changes'], payload['subject'], candidate['subject'], reviewed, candidate_details)
                if any(not any(within(path, scope) for scope in payload['paths']) for path in work['mechanical_changes']): reasons.append('mechanical-change-outside-reviewed-scope')
        if not same_tree or candidate['quality_run_id'] is not None:
            if candidate_gate.get('status') != 'passed': reasons.append('candidate-quality-gate-not-passed')
            if candidate_gate.get('status') in (None,'unverifiable'): unknown = True
            if (candidate_gate.get('subject') != candidate['subject'] or candidate_gate.get('wp_id') != payload['wp_id'] or
                    candidate_gate.get('wp_revision') != payload['wp_revision'] or candidate_gate.get('evidence_id') != candidate['quality_run_id']):
                reasons.append('candidate-quality-binding-mismatch')
        if len({ref['id'] for ref in payload['contract_refs']}) != len(payload['contract_refs']): reasons.append('duplicate-contract-reference')
        for ref in payload['contract_refs']:
            current = derived['registry'].get(ref['id'])
            if not current or any(current[k] != ref[k] for k in ('version','sha256')): reasons.append('contract-version-mismatch:' + ref['id'])
        for deviation_id in payload['deviation_refs']:
            deviation = derived['deviations'].get(deviation_id)
            if not deviation: reasons.append('unknown-deviation:' + deviation_id); continue
            if deviation['wp_id'] != payload['wp_id'] or deviation['wp_revision'] != payload['wp_revision']:
                reasons.append('deviation-work-package-mismatch:' + deviation_id)
            if any(not any(within(path, scope) for scope in payload['paths']) for path in deviation['scope_paths']):
                reasons.append('deviation-scope-mismatch:' + deviation_id)
            if deviation['status'] == 'closed':
                closure = deviation['closure']; closure_gate = quality.get('closures', {}).get(deviation_id, {}).get('gate', {})
                if closure is None: reasons.append('deviation-closure-missing:' + deviation_id)
                else:
                    if (closure['subject'] != payload['subject'] or set(closure['scope_paths']) != set(deviation['scope_paths']) or
                            closure_gate.get('subject') != closure['subject'] or closure_gate.get('gate_id') != closure['gate_id'] or
                            closure_gate.get('evidence_id') != closure['quality_run_id'] or closure_gate.get('wp_id') != payload['wp_id'] or
                            closure_gate.get('wp_revision') != payload['wp_revision']): reasons.append('deviation-closure-binding-mismatch:' + deviation_id)
                if closure_gate.get('status') != 'passed': reasons.append('deviation-closure-gate-not-passed:' + deviation_id)
                if closure_gate.get('status') in (None,'unverifiable'): unknown = True
            else:
                result['active_deviations'].append(deviation_id)
                if deviation['closure'] is not None: reasons.append('open-deviation-claims-closure:' + deviation_id)
                if timestamp(deviation['expires_at']) <= timestamp(at): reasons.append('expired-deviation:' + deviation_id)
                if deviation['subject_commit'] != payload['subject']['commit']: reasons.append('deviation-object-mismatch:' + deviation_id)
            if deviation['baseline'] is not None:
                analysis = baseline_analysis(reviewed, quality.get('baselines',{}).get(deviation_id,{}), deviation['baseline'], payload['wp_id'])
                result['failure_analysis'].append(dict(analysis, deviation_id=deviation_id))
        if gate.get('status') != 'passed': reasons.append('quality-gate-not-passed')
        if gate.get('status') in (None,'unverifiable'): unknown = True
        if gate.get('wp_id') != payload['wp_id'] or gate.get('wp_revision') != payload['wp_revision'] or gate.get('subject') != payload['subject']:
            reasons.append('quality-gate-object-mismatch')
        if gate.get('evidence_id') != payload['quality_run_id']: reasons.append('quality-run-mismatch')
        if gate.get('gate_id') != signoff['payload']['gate_id'] or gate.get('evidence_sha256') != signoff['payload']['evidence_sha256']:
            reasons.append('signoff-quality-binding-mismatch')
    result['reasons'] = sorted(set(reasons)); result['active_deviations'].sort()
    result['status'] = 'unverifiable' if unknown else ('rejected' if reasons else 'effective')
    return result
