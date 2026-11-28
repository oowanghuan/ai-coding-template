"""Deterministic lifecycle inside the existing single-host authority.

All observations must come from the reviewed controller, not model output.
This module does not authenticate remote workers or execute provider commands.
"""
import copy
import re
from datetime import timedelta

from framework.core.protocol import timestamp

STATES = {'available', 'running', 'quota_limited', 'suspended', 'offline',
          'recovering', 'authentication_required', 'disabled'}
LIMITS = {'rate_limited', 'quota_limited'}
LIVE = ('reserved', 'active')


def resource(config):
    value = config.get('resource', {})
    if not isinstance(value, dict) or set(value) - {'agent_tool', 'model_provider', 'model', 'credential_ref'}:
        raise ValueError('invalid resource selection')
    for item in value.values():
        if item is not None and (not isinstance(item, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,127}', item)):
            raise ValueError('resource metadata must be opaque references, never credential content')
    return {key: value.get(key) for key in ('agent_tool', 'model_provider', 'model', 'credential_ref')}


def row(rows, key):
    for value in rows:
        if value['id'] == key:
            return value
    raise ValueError('unknown identity: ' + key)


def stamp(at, seconds):
    return (timestamp(at) + timedelta(seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')


def check(state):
    runtime = state.get('worker_runtime')
    if runtime is None:
        return
    if set(runtime) != {'format', 'workers', 'groups', 'policy'} or runtime['format'] != 'worker-runtime/1':
        raise ValueError('invalid worker runtime')
    for identity, worker in runtime['workers'].items():
        row(state['snapshot']['workers'], identity)
        if worker['status'] not in STATES or worker['mode'] not in ('dedicated', 'elastic', 'restricted'):
            raise ValueError('invalid worker lifecycle state/mode')
        if worker['quota_group'] not in runtime['groups']:
            raise ValueError('missing quota group')
        timestamp(worker['heartbeat_at'])


def enable(state, payload, at):
    if 'worker_runtime' in state:
        raise ValueError('runtime already configured; no implicit overwrite')
    policy = dict(heartbeat_timeout=120, initial_backoff=60, max_backoff=900, max_probes=8)
    for key, value in payload.get('policy', {}).items():
        if key not in policy or type(value) is not int or not 1 <= value <= 86400:
            raise ValueError('invalid bounded policy')
        policy[key] = value
    if policy['initial_backoff'] > policy['max_backoff']:
        raise ValueError('backoff bounds inverted')
    runtime = {'format': 'worker-runtime/1', 'workers': {}, 'groups': {}, 'policy': policy}
    for config in payload['workers']:
        worker = row(state['snapshot']['workers'], config['worker_id'])
        key = worker['id']
        if key in runtime['workers'] or not config['quota_group'] or not config['auth_identity']:
            raise ValueError('duplicate worker or missing quota/identity binding')
        mode = config.get('mode', 'dedicated')
        if mode not in ('dedicated', 'elastic', 'restricted'):
            raise ValueError('invalid contribution mode')
        active = any(a['worker_ref'] == key and a['state'] in LIVE for a in state['snapshot']['assignments'])
        status = 'running' if active else ('available' if worker['state'] == 'available' and worker['quota'] == 'available' else 'recovering')
        runtime['workers'][key] = dict(status=status, quota_group=config['quota_group'],
            auth_identity=config['auth_identity'], resource=resource(config), mode=mode, heartbeat_at=at,
            authenticated=config.get('authenticated') is True, authorized=config.get('authorized') is True,
            host_available=worker['state'] in ('available', 'busy'),
            owner_hold={'paused': 'suspended', 'retired': 'disabled'}.get(worker['state']),
            reason=None, stop_confirmed=not active, last_observation=None)
        group = runtime['groups'].setdefault(config['quota_group'], dict(limited=False, reason=None,
            retry_at=None, next_probe_at=None, attempts=0, pending_probe=None, generation=0))
        if worker['quota'] != 'available':
            group.update(limited=True, reason='quota_' + worker['quota'], next_probe_at=stamp(at, policy['initial_backoff']))
    if set(runtime['workers']) != {w['id'] for w in state['snapshot']['workers']}:
        raise ValueError('all workers require explicit quota and identity bindings')
    state['worker_runtime'] = runtime
    # Unverified admission must not keep live write authority.
    for identity, value in runtime['workers'].items():
        if not value['authenticated'] or not value['authorized'] or runtime['groups'][value['quota_group']]['limited']:
            fence(state, [identity], 'runtime-admission-required')
        refresh(state, identity)
    check(state)
    return {'registered': sorted(runtime['workers']), 'execution_started': False}


def fence(state, identities, reason):
    """Invalidate authority immediately; never infer that a process has stopped."""
    for assignment in state['snapshot']['assignments']:
        if assignment['worker_ref'] not in identities or assignment['state'] not in LIVE:
            continue
        assignment.update(state='revoked', revocation_reason=reason)
        wp = row(state['snapshot']['work_packages'], assignment['wp_ref'])
        wp.update(state='paused', revision=wp['revision'] + 1)
        workspace = state['workspaces'][assignment['workspace_id']]
        if workspace['state'] != 'planned':
            workspace['handoff_required'] = True
        if workspace['state'] not in ('planned', 'prepared', 'finished'):
            workspace['state'] = 'unknown'
        if workspace['state'] not in ('planned', 'prepared', 'finished', 'stopped'):
            state['worker_runtime']['workers'][assignment['worker_ref']]['stop_confirmed'] = False


def refresh(state, identity):
    runtime = state['worker_runtime']
    w = runtime['workers'][identity]
    group = runtime['groups'][w['quota_group']]
    if w['owner_hold']:
        status = w['owner_hold']
    elif not w['host_available']:
        status = 'offline'
    elif not w['authenticated']:
        status = 'authentication_required'
    elif not w['authorized'] or state['snapshot']['project']['paused'] or state['snapshot']['project']['budget'] != 'available':
        status = 'suspended'
    elif group['limited']:
        status = 'quota_limited'
    elif not w['stop_confirmed'] and not any(a['worker_ref'] == identity and a['state'] in LIVE for a in state['snapshot']['assignments']):
        status = 'recovering'
    else:
        status = 'running' if any(a['worker_ref'] == identity and a['state'] in LIVE for a in state['snapshot']['assignments']) else 'available'
    w['status'] = status
    # A compatibility projection, never a second lifecycle authority.
    old = row(state['snapshot']['workers'], identity)
    old['state'] = {'running': 'busy', 'available': 'available', 'disabled': 'retired', 'offline': 'offline'}.get(status, 'paused')
    old['quota'] = 'exhausted' if group['limited'] else 'available'
    return status


def observe(state, payload, at):
    runtime = state['worker_runtime']
    identity = payload['worker_id']
    w = runtime['workers'][identity]
    event = payload['event']
    if event == 'probe-result' and type(payload.get('available')) is not bool:
        raise ValueError('probe available must be explicit boolean')
    group = runtime['groups'][w['quota_group']]
    siblings = [key for key, value in runtime['workers'].items() if value['quota_group'] == w['quota_group']]
    w['last_observation'] = {'at': at, 'event': event, 'source': payload.get('source', 'controller')}
    if event in LIMITS:
        retry = payload.get('retry_at')
        if retry is not None:
            timestamp(retry)
        if not group['limited']:
            group.update(attempts=0, pending_probe=None,
                         next_probe_at=stamp(at, runtime['policy']['initial_backoff']))
        # Each distinct committed observation supersedes prior availability
        # evidence. Store operation replay does not re-enter this function.
        # Keep an outstanding probe until its actual response is reconciled:
        # superseding its result is not cancellation of the external operation.
        group['generation'] += 1
        group.update(limited=True, reason=event)
        if retry is not None:
            group['retry_at'] = max(group['retry_at'] or retry, retry)
            group['next_probe_at'] = max(group['next_probe_at'] or at, group['retry_at'])
        fence(state, siblings, event)
    elif event in ('offline', 'network_error'):
        w.update(host_available=False, reason=event)
        fence(state, [identity], event)
    elif event == 'authentication_required':
        w.update(authenticated=False, reason=event)
        fence(state, [identity], event)
    elif event in ('suspend', 'disable'):
        w['owner_hold'] = 'suspended' if event == 'suspend' else 'disabled'
        fence(state, [identity], event)
    elif event == 'resume':
        w['owner_hold'] = None
    elif event == 'heartbeat':
        w.update(heartbeat_at=at, host_available=True)
    elif event == 'credentials-verified':
        w.update(authenticated=payload['authenticated'] is True, authorized=payload['authorized'] is True)
        if not w['authenticated'] or not w['authorized']:
            fence(state, [identity], 'credential-check-failed')
    elif event in ('context_exhausted', 'interrupted', 'budget_exhausted'):
        if event == 'budget_exhausted' and payload.get('budget_scope') not in ('project', 'invocation', 'session'):
            raise ValueError('explicit trusted budget scope required')
        fence(state, [identity], event)
        w['reason'] = event
        if event == 'budget_exhausted' and payload['budget_scope'] == 'project':
            if payload.get('source') != 'project-budget-controller':
                raise ValueError('project budget controller observation required')
            state['snapshot']['project']['budget'] = 'exhausted'
            fence(state, list(runtime['workers']), event)
    elif event == 'probe-result':
        if group['pending_probe'] is None or payload['probe_id'] != group['pending_probe']:
            raise ValueError('stale/unknown probe result')
        issued = re.fullmatch(r'probe:' + re.escape(w['quota_group']) + r':(0|[1-9][0-9]*):([1-9][0-9]*)', group['pending_probe'])
        if (issued is None or int(issued[1]) > group['generation'] or
                int(issued[2]) != group['attempts']):
            raise ValueError('invalid pending probe generation/attempt')
        stale_probe_result = int(issued[1]) < group['generation']
        group['pending_probe'] = None
        if stale_probe_result:
            # Receipt of this old response resolves only its outstanding intent.
            # Neither success nor failure changes the newer limit/backoff/budget.
            pass
        elif payload.get('available') is True:
            group.update(limited=False, reason=None, retry_at=None, next_probe_at=None)
        else:
            delay = min(runtime['policy']['max_backoff'], runtime['policy']['initial_backoff'] * 2 ** min(group['attempts'], 16))
            group['next_probe_at'] = stamp(at, delay)
    else:
        raise ValueError('unsupported worker event')
    for key in runtime['workers']:
        refresh(state, key)
    result = {'worker_id': identity, 'status': w['status'], 'group': copy.deepcopy(group)}
    if event == 'probe-result':
        result['stale_probe_result'] = stale_probe_result
    return result


def tick(state, at, create_probes=True):
    runtime = state['worker_runtime']
    probes = []
    for identity, w in runtime['workers'].items():
        if timestamp(w['heartbeat_at']) + timedelta(seconds=runtime['policy']['heartbeat_timeout']) <= timestamp(at):
            w['host_available'] = False
            fence(state, [identity], 'heartbeat-expired')
    for key, group in runtime['groups'].items():
        eligible = any(w['quota_group'] == key and w['authenticated'] and w['authorized'] and
                       w['host_available'] and not w['owner_hold'] for w in runtime['workers'].values())
        project = state['snapshot']['project']
        if (create_probes and group['limited'] and not group['pending_probe'] and eligible and not project['paused'] and
            project['budget'] == 'available' and group['next_probe_at'] is not None and
            timestamp(group['next_probe_at']) <= timestamp(at) and group['attempts'] < runtime['policy']['max_probes']):
            group['attempts'] += 1
            group['pending_probe'] = 'probe:%s:%s:%s' % (key, group['generation'], group['attempts'])
            probes.append({'group': key, 'probe_id': group['pending_probe']})
    for key in runtime['workers']:
        refresh(state, key)
    return {'probes': probes, 'model_calls': 0}


def claimable(state, identity, at):
    runtime = state.get('worker_runtime')
    if runtime is not None:
        w = runtime['workers'][identity]
        if timestamp(w['heartbeat_at']) + timedelta(seconds=runtime['policy']['heartbeat_timeout']) <= timestamp(at):
            raise ValueError('worker heartbeat expired')
        if refresh(state, identity) not in ('available', 'running'):
            raise ValueError('worker lifecycle blocks new work')
