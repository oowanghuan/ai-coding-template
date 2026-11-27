"""Pure validation of declared snapshots, not an authority, scheduler or evidence Gate."""
import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry

SCHEMA_PATH = Path(__file__).resolve().parents[2] / 'schemas/protocol.schema.json'
MINIMUM = {
    'spec': {'review_passed', 'spec_ratified', 'archived'},
    'code': {'review_passed', 'merged', 'engineering_accepted'},
    'review': {'review_recorded'},
    'release': {'review_passed', 'engineering_accepted', 'deployed', 'health_checked', 'rollback_verified'},
    'business-validation': {'business_validated'},
}
EDGES = {
    'planned': {'ready', 'blocked', 'cancelled'},
    'ready': {'in_progress', 'blocked', 'paused', 'cancelled'},
    'in_progress': {'submitted', 'blocked', 'paused', 'cancelled'},
    'submitted': {'in_review', 'in_progress', 'blocked', 'paused', 'cancelled'},
    'in_review': {'accepted', 'in_progress', 'blocked', 'paused', 'cancelled'},
    'accepted': {'closed', 'in_progress'},
    'closed': {'in_progress'},
    'blocked': {'planned', 'ready', 'in_progress', 'cancelled'},
    'paused': {'planned', 'ready', 'in_progress', 'cancelled'},
    'cancelled': set(),
}


def timestamp(value):
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def load_json(path):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Non-JSON number: ' + x)))


def within(path, scope):
    """Literal file or trailing-slash directory prefixes, never globs."""
    return path == scope or (scope.endswith('/') and path.startswith(scope))


def overlap(a, b):
    return within(a, b) or within(b, a)


def schema_errors(snapshot):
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    checker = FormatChecker()

    @checker.checks('date-time', raises=(ValueError, TypeError))
    def utc_time(value):
        return bool(timestamp(value))

    # Empty registry has no remote retrieval callback. All references are local $defs.
    validator = Draft202012Validator(schema, format_checker=checker, registry=Registry())
    return sorted('schema:' + '/'.join(map(str, e.absolute_path)) + ': ' + e.message
                  for e in validator.iter_errors(snapshot))


def validate(snapshot, at):
    """Return stable errors at an explicit UTC observation time; never mutate input."""
    now = timestamp(at)
    errors = schema_errors(snapshot)
    if errors:
        return sorted(errors)

    def require(condition, message):
        if not condition:
            errors.append(message)

    tables = {}
    all_ids = set()
    for group in ('roles', 'providers', 'hosts', 'workers', 'sessions', 'authorizations',
                  'work_packages', 'assignments', 'checkpoints'):
        tables[group] = {}
        for item in snapshot[group]:
            require(item['id'] not in all_ids, 'duplicate-id:' + item['id'])
            all_ids.add(item['id'])
            tables[group][item['id']] = item
    if errors:
        return sorted(errors)

    def lookup(group, key, context):
        value = tables[group].get(key)
        require(value is not None, 'missing-reference:' + context + ':' + str(key))
        return value

    project = snapshot['project']
    principals = set(project['owner_principals']) | {w['principal'] for w in snapshot['workers']}
    for worker in snapshot['workers']:
        lookup('providers', worker['provider_ref'], worker['id'])
        lookup('hosts', worker['host_ref'], worker['id'])
        for role in worker['role_refs']:
            lookup('roles', role, worker['id'])
    for session in snapshot['sessions']:
        worker = lookup('workers', session['worker_ref'], session['id'])
        if worker:
            require(all(session[k] == worker[k] for k in ('host_ref', 'provider_ref')),
                    'session-environment:' + session['id'])
    for auth in snapshot['authorizations']:
        require(auth['issuer'] in project['owner_principals'], 'authorization-issuer:' + auth['id'])
        for group, field in [('work_packages', 'wp_refs'), ('roles', 'role_refs'), ('hosts', 'environment_refs')]:
            for key in auth[field]:
                lookup(group, key, auth['id'])

    for wp in snapshot['work_packages']:
        key = wp['id']
        require(wp['project_id'] == project['id'], 'project-mismatch:' + key)
        lookup('roles', wp['accountable_role'], key)
        for field in ('implementer', 'reviewer', 'acceptor', 'merger'):
            require(wp[field] is None or wp[field] in principals, 'unknown-principal:' + key + ':' + field)
        required = set(wp['required_milestones'])
        require(MINIMUM[wp['kind']] <= required, 'missing-kind-milestones:' + key)
        require(required <= set(wp['milestones']), 'undefined-milestone:' + key)
        if wp['state'] in ('planned', 'ready'):
            require(not any(m['status'] == 'passed' for m in wp['milestones'].values()),
                    'unstarted-with-completion:' + key)
        for name, milestone in wp['milestones'].items():
            if milestone['status'] == 'passed':
                require(wp['submitted_sha'] is not None and milestone['subject_sha'] == wp['submitted_sha'],
                        'milestone-sha:' + key + ':' + name)
                require(bool(milestone['evidence_refs']) and milestone['signer'] in principals,
                        'empty-signoff:' + key + ':' + name)
                signer_field = {'review_passed': 'reviewer', 'review_recorded': 'reviewer',
                                'spec_ratified': 'acceptor', 'engineering_accepted': 'acceptor',
                                'business_validated': 'acceptor', 'merged': 'merger'}.get(name)
                if signer_field:
                    require(milestone['signer'] == wp[signer_field], 'wrong-signer:' + key + ':' + name)
            if milestone['status'] == 'not_applicable':
                require(bool(milestone['reason']) and name not in required, 'required-not-applicable:' + key)
        if wp['state'] in ('submitted', 'in_review', 'accepted', 'closed'):
            require(wp['submitted_sha'] is not None and bool(wp['evidence_refs']), 'missing-delivery:' + key)
        if wp['state'] in ('accepted', 'closed'):
            require(all(wp['milestones'].get(m, {}).get('status') == 'passed' for m in required),
                    'unmet-acceptance:' + key)
            require(bool(wp['review_refs']), 'missing-review-record:' + key)
        if wp['risk'] == 'high' and (wp['state'] in ('ready', 'in_progress', 'submitted', 'in_review', 'accepted', 'closed')
                                    or any(m['status'] == 'passed' for m in wp['milestones'].values())):
            require(all(wp[f] is not None for f in ('implementer', 'reviewer', 'acceptor')) and
                    wp['implementer'] not in (wp['reviewer'], wp['acceptor']), 'independence:' + key)
        if wp['authorization_ref'] is not None:
            lookup('authorizations', wp['authorization_ref'], key)
        if wp['assignment_ref'] is not None:
            assignment = lookup('assignments', wp['assignment_ref'], key)
            if assignment:
                require(assignment['wp_ref'] == key, 'assignment-backref:' + key)
        if wp['checkpoint_ref'] is not None:
            cp = lookup('checkpoints', wp['checkpoint_ref'], key)
            if cp:
                require(cp['wp_ref'] == key, 'checkpoint-backref:' + key)
        for dep in wp['dependencies']:
            other = lookup('work_packages', dep['wp_id'], key)
            if other:
                require(dep['required_milestone'] in other['milestones'], 'dependency-milestone:' + key)
                if wp['state'] in ('ready', 'in_progress'):
                    milestone = other['milestones'].get(dep['required_milestone'], {})
                    require(milestone.get('status') == 'passed' and
                            milestone.get('subject_sha') == dep['artifact_revision'], 'dependency-not-ready:' + key)
        if wp['state'] in ('ready', 'in_progress'):
            auth = tables['authorizations'].get(wp['authorization_ref'])
            require(not project['paused'] and project['budget'] == 'available' and not wp['blocking_conditions'],
                    'project-or-task-blocked:' + key)
            require(auth is not None and auth['state'] == 'granted' and timestamp(auth['expires_at']) > now
                    and key in auth['wp_refs'] and wp['accountable_role'] in auth['role_refs'],
                    'not-authorized:' + key)
            if auth:
                require(all(any(within(p, s) for s in auth['allowed_paths']) for p in wp['allowed_paths'])
                        and set(wp['external_effects']) <= set(auth['external_effects']), 'authorization-scope:' + key)
            if wp['state'] == 'in_progress':
                assignment = tables['assignments'].get(wp['assignment_ref'])
                require(assignment is not None and assignment['state'] == 'active', 'no-active-assignment:' + key)

    # Iterative DFS avoids a Python recursion limit on long dependency chains.
    visited, visiting = set(), set()
    for root in tables['work_packages']:
        stack = [(root, False)]
        while stack:
            key, leaving = stack.pop()
            if leaving:
                visiting.discard(key)
                visited.add(key)
                continue
            if key in visiting:
                errors.append('dependency-cycle:' + key)
                continue
            if key in visited or key not in tables['work_packages']:
                continue
            visiting.add(key)
            stack.append((key, True))
            stack.extend((d['wp_id'], False) for d in tables['work_packages'][key]['dependencies'])

    active = []
    for assignment in snapshot['assignments']:
        key = assignment['id']
        wp = lookup('work_packages', assignment['wp_ref'], key)
        worker = lookup('workers', assignment['worker_ref'], key)
        session = lookup('sessions', assignment['session_ref'], key)
        lookup('roles', assignment['role_ref'], key)
        if not wp or not worker or not session:
            continue
        require(session['worker_ref'] == worker['id'] and assignment['role_ref'] in worker['role_refs'],
                'assignment-worker-binding:' + key)
        require(assignment['base_sha'] == wp['baseline_sha'], 'assignment-baseline:' + key)
        require(assignment['role_ref'] == wp['accountable_role'], 'assignment-role:' + key)
        require(all(any(within(p, s) for s in wp['allowed_paths']) for p in assignment['allowed_paths']) and
                not any(overlap(p, f) for p in assignment['allowed_paths'] for f in wp['forbidden_paths']),
                'assignment-scope:' + key)
        if assignment['last_checkpoint'] is not None:
            cp = lookup('checkpoints', assignment['last_checkpoint'], key)
            if cp:
                require(cp['assignment_ref'] == key, 'assignment-checkpoint:' + key)
        if assignment['state'] != 'active':
            continue
        active.append(assignment)
        require(wp['state'] == 'in_progress' and wp['assignment_ref'] == key and
                wp['implementer'] == worker['principal'], 'active-assignment-binding:' + key)
        require(assignment['authority_epoch'] == project['authority_epoch'] and
                timestamp(assignment['heartbeat_at']) <= now < timestamp(assignment['lease_expires_at']),
                'inactive-lease:' + key)
        require(worker['state'] in ('available', 'busy') and worker['quota'] == 'available', 'worker-unavailable:' + key)
        auth = tables['authorizations'].get(wp['authorization_ref'])
        require(auth is not None and worker['host_ref'] in auth['environment_refs'], 'host-not-authorized:' + key)
    for i, a in enumerate(active):
        for b in active[i + 1:]:
            require(a['wp_ref'] != b['wp_ref'], 'double-assignment:' + a['wp_ref'])
            require(a['workspace_id'] != b['workspace_id'], 'shared-workspace:' + a['id'])
            require(not any(overlap(p, q) for p in a['allowed_paths'] for q in b['allowed_paths']),
                    'scope-conflict:' + a['id'] + ':' + b['id'])
    for worker in snapshot['workers']:
        require(sum(a['worker_ref'] == worker['id'] for a in active) <= worker['slots'], 'worker-capacity:' + worker['id'])

    for cp in snapshot['checkpoints']:
        key = cp['id']
        wp = lookup('work_packages', cp['wp_ref'], key)
        assignment = lookup('assignments', cp['assignment_ref'], key)
        lookup('roles', cp['role_ref'], key)
        lookup('authorizations', cp['authorization_ref'], key)
        require(timestamp(cp['created_at']) <= now, 'future-checkpoint:' + key)
        if wp and assignment:
            require(cp['wp_revision'] <= wp['revision'] and assignment['wp_ref'] == wp['id'] and
                    cp['role_ref'] == assignment['role_ref'] and cp['baseline_sha'] == assignment['base_sha'],
                    'checkpoint-binding:' + key)
            if wp['checkpoint_ref'] == key and wp['state'] in ('ready', 'in_progress'):
                require(not cp['unknown_operations'], 'unknown-operation:' + key)
                require(cp['authorization_ref'] == wp['authorization_ref'] and cp['spec_refs'] == wp['spec_refs'],
                        'stale-checkpoint-contract:' + key)
                require(cp['lease_expires_at'] == assignment['lease_expires_at'], 'stale-checkpoint-lease:' + key)
    return sorted(set(errors))


def validate_transition(before, after, at):
    """Validate a proposed snapshot revision. Does not commit it or grant execution rights."""
    # The old snapshot can have expired leases by now; otherwise recording a pause
    # or revocation would be impossible. Its shape is checked; the new state must
    # satisfy all current invariants. This function does not authenticate history.
    errors = schema_errors(before) + validate(after, at)
    if errors:
        return sorted(set(errors))
    if before['project']['id'] != after['project']['id'] or after['project']['revision'] != before['project']['revision'] + 1:
        errors.append('project-revision')
    old = {w['id']: w for w in before['work_packages']}
    new = {w['id']: w for w in after['work_packages']}
    if not old.keys() <= new.keys():
        errors.append('work-package-deletion')
    if len(old) != len(before['work_packages']):
        errors.append('duplicate-old-work-package')
    if after['project']['authority_epoch'] < before['project']['authority_epoch']:
        errors.append('authority-epoch-regressed')
    previous_assignments = {a['id']: a for a in before['assignments']}
    for assignment in after['assignments']:
        previous = previous_assignments.get(assignment['id'])
        if previous:
            if any(assignment[k] != previous[k] for k in ('wp_ref', 'worker_ref', 'session_ref', 'role_ref',
                                                         'authority_epoch', 'fencing_token', 'workspace_id',
                                                         'base_sha', 'allowed_paths')):
                errors.append('assignment-identity-changed:' + assignment['id'])
            if previous['state'] != 'active' and assignment['state'] == 'active':
                errors.append('assignment-reactivated:' + assignment['id'])
        else:
            earlier = [a['fencing_token'] for a in before['assignments']
                       if a['wp_ref'] == assignment['wp_ref'] and a['authority_epoch'] == assignment['authority_epoch']]
            if earlier and assignment['fencing_token'] <= max(earlier):
                errors.append('fencing-token-not-increased:' + assignment['id'])
    for key in old.keys() & new.keys():
        a, b = old[key], new[key]
        if a == b:
            continue
        if b['revision'] != a['revision'] + 1:
            errors.append('work-package-revision:' + key)
        if a['state'] != b['state'] and b['state'] not in EDGES[a['state']]:
            errors.append('illegal-transition:' + key)
        if a['kind'] != b['kind'] or not set(a['required_milestones']) <= set(b['required_milestones']):
            errors.append('acceptance-policy-weakened:' + key)
        if ['low', 'medium', 'high'].index(b['risk']) < ['low', 'medium', 'high'].index(a['risk']):
            errors.append('risk-policy-weakened:' + key)
        material = any(a[k] != b[k] for k in ('submitted_sha', 'spec_refs', 'positive_criteria', 'negative_criteria',
                                            'allowed_paths', 'forbidden_paths', 'objective', 'deliverables'))
        signed = [m for m, value in a['milestones'].items() if value['status'] == 'passed']
        if material and signed:
            if b['state'] != 'in_progress' or not b['change_reason'] or any(
                    b['milestones'].get(m, {}).get('status') != 'invalidated' for m in signed):
                errors.append('signature-invalidation-required:' + key)
        if b['state'] == 'in_progress' and a['state'] in ('submitted', 'in_review', 'accepted', 'closed') and not b['change_reason']:
            errors.append('missing-rework-reason:' + key)
    return sorted(set(errors))
