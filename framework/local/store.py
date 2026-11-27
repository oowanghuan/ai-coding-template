"""Atomic, credential-free local controller for cooperative workers of one OS owner."""
import base64
import copy
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import re
import uuid

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from framework.core.protocol import load_json, validate, schema_errors, overlap, within, timestamp
from framework.local.storage import authority_lock, atomic_json, check_install_journal, fingerprint, root_path, safe_path

ROOT = Path(__file__).resolve().parents[2]
LIVE = ('reserved', 'active')
UNKNOWN = ('creating', 'launching', 'running', 'unknown')


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def find(rows, key):
    for row in rows:
        if row['id'] == key:
            return row
    raise ValueError('unknown identifier: ' + str(key))


def envelope(snapshot, store_id=None):
    snapshot = copy.deepcopy(snapshot)
    if snapshot['schema_version'] not in ('0.1', '0.2'):
        raise ValueError('unsupported import version')
    snapshot['schema_version'] = '0.2'  # Explicit import into the local-state/1 envelope.
    counters = {}
    for assignment in snapshot['assignments']:
        counters[assignment['wp_ref']] = max(counters.get(assignment['wp_ref'], 0), assignment['fencing_token'])
    return dict(format='local-state/1', store_id=store_id or uuid.uuid4().hex, revision=0,
                snapshot=snapshot, operations={}, workspaces={}, tokens=counters, deliveries={})


def shape(state):
    core = load_json(ROOT / 'schemas/protocol.schema.json')
    local = load_json(ROOT / 'schemas/local-state.schema.json')
    registry = Registry().with_resource(core['$id'], Resource.from_contents(core))
    errors = list(Draft202012Validator(local, registry=registry).iter_errors(state))
    if errors:
        raise ValueError('invalid local state: ' + errors[0].message)
    if state['snapshot']['schema_version'] != '0.2':
        raise ValueError('local authority requires explicit protocol 0.2 import')
    errors = schema_errors(state['snapshot'])
    if errors:
        raise ValueError(errors[0])
    assignments = {a['id']: a for a in state['snapshot']['assignments']}
    for key, workspace in state['workspaces'].items():
        assignment = assignments.get(workspace['assignment_id'])
        if (workspace['id'] != key or workspace['path'] != '.ai-org/workspaces/' + key or
                assignment is None or assignment['workspace_id'] != key or
                assignment['wp_ref'] != workspace['wp_id'] or assignment['base_sha'] != workspace['baseline_sha']):
            raise ValueError('workspace registry binding mismatch')
    for assignment in assignments.values():
        if state['tokens'].get(assignment['wp_ref'], 0) < assignment['fencing_token']:
            raise ValueError('fencing counter regressed')


class Store:
    def __init__(self, root):
        self.root = root_path(root)
        self.path = safe_path(self.root, '.ai-org/state.json')

    def _read(self):
        check_install_journal(self.root)
        safe_path(self.root, '.ai-org/state.json')
        if self.path.stat().st_nlink != 1:
            raise ValueError('linked authority file refused')
        state = load_json(self.path)
        shape(state)
        return state

    def inspect(self, at=None):
        with authority_lock(self.root):
            state = self._read()
        return {'state': state, 'observed_at': at or now(),
                'consistency_errors': validate(state['snapshot'], at or now())}

    def initialize(self, snapshot, actor, at=None):
        if actor not in snapshot['project']['owner_principals']:
            raise ValueError('owner controller required')
        if snapshot['project']['state_backend'] != 'local_git':
            raise ValueError('local controller cannot import another authority backend')
        state = envelope(snapshot)
        if any(a['state'] in LIVE for a in snapshot['assignments']):
            raise ValueError('cannot import live execution rights')
        errors = validate(state['snapshot'], at or now())
        if errors:
            raise ValueError('; '.join(errors))
        with authority_lock(self.root, create=True):
            check_install_journal(self.root)
            if self.path.exists():
                raise ValueError('authority already exists; explicit migration required')
            atomic_json(self.path, state)
        return state

    @staticmethod
    def _owner(state, actor):
        if actor not in state['snapshot']['project']['owner_principals']:
            raise ValueError('owner controller required')

    @staticmethod
    def _credential(state, payload, actor, at, states=LIVE):
        if type(payload['epoch']) is not int or type(payload['token']) is not int:
            raise ValueError('epoch/token must be integers')
        assignment = find(state['snapshot']['assignments'], payload['assignment_id'])
        worker = find(state['snapshot']['workers'], assignment['worker_ref'])
        if actor != worker['principal']:
            raise ValueError('worker principal mismatch')
        if (assignment['state'] not in states or payload['epoch'] != assignment['authority_epoch'] or
                payload['token'] != assignment['fencing_token'] or
                assignment['authority_epoch'] != state['snapshot']['project']['authority_epoch'] or
                timestamp(assignment['lease_expires_at']) <= timestamp(at)):
            raise ValueError('fenced or expired assignment')
        wp = find(state['snapshot']['work_packages'], assignment['wp_ref'])
        if wp['assignment_ref'] != assignment['id']:
            raise ValueError('assignment no longer owns task')
        return assignment, wp, worker

    @staticmethod
    def _unresolved(state, wp_id):
        return any(w['wp_id'] == wp_id and w['state'] in UNKNOWN for w in state['workspaces'].values())

    @staticmethod
    def _expire(state, at):
        for assignment in state['snapshot']['assignments']:
            if assignment['state'] in LIVE and timestamp(assignment['lease_expires_at']) <= timestamp(at):
                assignment['state'] = 'expired'
                wp = find(state['snapshot']['work_packages'], assignment['wp_ref'])
                if wp['assignment_ref'] == assignment['id']:
                    wp['state'] = 'paused'
                    wp['revision'] += 1

    def change(self, action, payload, actor, expected_revision, operation_id, at=None, fault=None):
        if not re.fullmatch(r'[A-Za-z0-9._:-]{1,128}', operation_id):
            raise ValueError('invalid operation_id')
        observed = at or now()
        intent = fingerprint({'action': action, 'payload': payload, 'actor': actor})
        with authority_lock(self.root):
            state = self._read()
            previous = state['operations'].get(operation_id)
            if previous:
                if previous['intent'] != intent:
                    raise ValueError('operation_id reused for a different intent')
                return {'replayed': True, 'revision': state['revision'], 'operation': previous}
            if expected_revision != state['revision']:
                raise ValueError('revision conflict')
            self._expire(state, observed)
            result = self._apply(state, action, payload, actor, observed)
            state['revision'] += 1
            state['snapshot']['project']['revision'] += 1
            errors = validate(state['snapshot'], observed)
            if errors:
                raise ValueError('; '.join(errors))
            receipt = {'intent': intent, 'action': action, 'actor': actor, 'at': observed,
                       'status': 'committed', 'result': result, 'revision': state['revision']}
            state['operations'][operation_id] = receipt
            shape(state)
            if fault:
                fault('before_commit')
            atomic_json(self.path, state)
            if fault:
                fault('after_commit')
            return {'replayed': False, 'revision': state['revision'], 'operation': receipt}

    def _apply(self, state, action, payload, actor, at):
        snapshot = state['snapshot']
        if action == 'register-worker':
            self._owner(state, actor)
            worker = payload['worker']
            if any(a['worker_ref'] == worker['id'] and a['state'] in LIVE for a in snapshot['assignments']):
                raise ValueError('cannot reconfigure an assigned worker')
            for group, field in [('providers', 'provider'), ('hosts', 'host'), ('workers', 'worker'), ('sessions', 'session')]:
                row = payload[field]
                existing = [r for r in snapshot[group] if r['id'] == row['id']]
                if existing and existing[0] != row:
                    raise ValueError('registered identity is immutable; register a new identity')
                if not existing:
                    snapshot[group].append(copy.deepcopy(row))
            return {'worker_id': worker['id']}
        if action == 'claim':
            wp = find(snapshot['work_packages'], payload['wp_id'])
            worker = find(snapshot['workers'], payload['worker_id'])
            session = find(snapshot['sessions'], payload['session_id'])
            if actor != worker['principal'] or session['worker_ref'] != worker['id']:
                raise ValueError('worker/session principal mismatch')
            if wp['state'] not in ('planned', 'ready', 'paused') or wp['blocking_conditions']:
                raise ValueError('task is not claimable')
            if self._unresolved(state, wp['id']):
                raise ValueError('unknown workspace/process outcome; reconcile before reassignment')
            if wp['checkpoint_ref'] and find(snapshot['checkpoints'], wp['checkpoint_ref'])['unknown_operations']:
                raise ValueError('checkpoint has unknown operations')
            if any(a['wp_ref'] == wp['id'] and a['state'] in LIVE for a in snapshot['assignments']):
                raise ValueError('task already claimed')
            if wp['kind'] not in worker['capabilities']:
                raise ValueError('worker capability mismatch')
            if not wp['baseline_sha']:
                raise ValueError('unknown baseline')
            seconds = payload['lease_seconds']
            if type(seconds) is not int or not 1 <= seconds <= 3600:
                raise ValueError('lease_seconds must be 1..3600')
            counter = state['tokens'].get(wp['id'], 0) + 1
            state['tokens'][wp['id']] = counter
            identity = 'assignment-' + uuid.uuid4().hex
            workspace = 'workspace-' + uuid.uuid4().hex
            lease = (timestamp(at) + timedelta(seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')
            assignment = dict(id=identity, wp_ref=wp['id'], worker_ref=worker['id'], session_ref=session['id'],
                              role_ref=wp['accountable_role'], authority_epoch=snapshot['project']['authority_epoch'],
                              fencing_token=counter, workspace_id=workspace, base_sha=wp['baseline_sha'],
                              allowed_paths=copy.deepcopy(wp['allowed_paths']), state='reserved', lease_expires_at=lease,
                              heartbeat_at=at, last_checkpoint=None, revocation_reason=None)
            snapshot['assignments'].append(assignment)
            wp.update(state='ready', assignment_ref=identity, implementer=actor, checkpoint_ref=None,
                      revision=wp['revision'] + 1)
            state['workspaces'][workspace] = {'id': workspace, 'wp_id': wp['id'], 'assignment_id': identity,
                                              'path': '.ai-org/workspaces/' + workspace,
                                              'baseline_sha': wp['baseline_sha'], 'state': 'planned', 'run': None}
            return {'assignment_id': identity, 'epoch': assignment['authority_epoch'], 'token': counter,
                    'lease_expires_at': lease, 'workspace_id': workspace}
        if action == 'revoke':
            self._owner(state, actor)
            assignment = find(snapshot['assignments'], payload['assignment_id'])
            if assignment['state'] not in LIVE:
                raise ValueError('assignment is not live')
            assignment.update(state='revoked', revocation_reason=payload['reason'])
            wp = find(snapshot['work_packages'], assignment['wp_ref'])
            wp.update(state='paused', revision=wp['revision'] + 1)
            return {'assignment_id': assignment['id'], 'state': 'revoked'}
        if action == 'reconcile':
            self._owner(state, actor)
            workspace = state['workspaces'][payload['workspace_id']]
            if workspace['state'] != 'creating' or payload['resolution'] != 'workspace-present':
                raise ValueError('only a pre-launch workspace can be reconciled automatically')
            from framework.local.runner import verify_workspace
            verify_workspace(self.root, workspace, pristine=True)
            workspace['state'] = 'prepared'
            return {'workspace_id': workspace['id'], 'state': 'prepared'}
        assignment, wp, worker = self._credential(state, payload, actor, at)
        workspace = state['workspaces'][assignment['workspace_id']]
        if action == 'heartbeat':
            seconds = payload['lease_seconds']
            if type(seconds) is not int or not 1 <= seconds <= 3600:
                raise ValueError('invalid lease duration')
            assignment['heartbeat_at'] = at
            assignment['lease_expires_at'] = (timestamp(at) + timedelta(seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')
            return {'lease_expires_at': assignment['lease_expires_at']}
        if action == 'release':
            if workspace['state'] in UNKNOWN:
                raise ValueError('cannot release an unresolved runner')
            assignment['state'] = 'released'
            wp.update(state='paused', revision=wp['revision'] + 1)
            return {'state': 'released'}
        if action == 'start':
            if assignment['state'] != 'reserved' or workspace['state'] != 'planned':
                raise ValueError('start requires a fresh reservation')
            assignment['state'] = 'active'
            wp.update(state='in_progress', revision=wp['revision'] + 1)
            workspace['state'] = 'creating'
            return {'workspace_id': workspace['id'], 'state': 'creating'}
        if action == 'submit':
            if assignment['state'] != 'active' or workspace['state'] not in ('prepared', 'finished'):
                raise ValueError('workspace is not ready for controlled delivery')
            relative = payload['path']
            if not any(within(relative, p) for p in assignment['allowed_paths']) or any(
                    within(relative, p) for p in wp['forbidden_paths']):
                raise ValueError('artifact outside assigned scope')
            path = safe_path(safe_path(self.root, workspace['path']), relative)
            if not path.is_file() or path.stat().st_nlink != 1 or path.stat().st_size > 65536:
                raise ValueError('artifact must be a regular single-link file of at most 64 KiB')
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if digest != payload['sha256']:
                raise ValueError('artifact changed')
            if wp['id'] in state['deliveries']:
                raise ValueError('delivery already exists')
            state['deliveries'][wp['id']] = {'assignment_id': assignment['id'], 'epoch': payload['epoch'],
                'token': payload['token'], 'path': relative, 'sha256': digest,
                'content_base64': base64.b64encode(data).decode(), 'baseline_sha': assignment['base_sha']}
            return {'delivery_id': wp['id'], 'sha256': digest, 'accepted': False}
        if action == 'run-begin':
            if assignment['state'] != 'active' or workspace['state'] != 'prepared' or workspace['run'] is not None:
                raise ValueError('runner already invoked or outcome unknown')
            relative = payload['path']
            safe_path(self.root, relative)
            if relative.split('/')[0] in ('.git', '.ai-org') or not any(
                    within(relative, p) for p in assignment['allowed_paths']) or any(
                    within(relative, p) for p in wp['forbidden_paths']):
                raise ValueError('synthetic output outside assigned scope')
            workspace.update(state='launching', run={'state': 'launching', 'path': relative,
                'content_sha256': payload['content_sha256'], 'started_at': at})
            return {'workspace_id': workspace['id']}
        raise ValueError('unknown action: ' + action)

    def guard(self, credentials, actor):
        with authority_lock(self.root):
            state = self._read()
            self._credential(state, credentials, actor, now(), states=('active',))
            errors = validate(state['snapshot'], now())
            if errors:
                raise ValueError('; '.join(errors))
            return state

    def workspace_phase(self, credentials, actor, expected, new, run=None, allow_fenced=False):
        """Trusted runner reconciliation only; not exposed as a caller-controlled CLI action."""
        with authority_lock(self.root):
            state = self._read()
            if allow_fenced:
                assignment = find(state['snapshot']['assignments'], credentials['assignment_id'])
                worker = find(state['snapshot']['workers'], assignment['worker_ref'])
                if (actor != worker['principal'] or credentials['token'] != assignment['fencing_token'] or
                        credentials['epoch'] != assignment['authority_epoch']):
                    raise ValueError('runner identity mismatch')
            else:
                assignment, _, _ = self._credential(state, credentials, actor, now(), states=('active',))
            workspace = state['workspaces'][assignment['workspace_id']]
            if workspace['state'] != expected:
                raise ValueError('workspace phase conflict')
            workspace['state'] = new
            if run is not None:
                workspace['run'] = run
            state['revision'] += 1
            state['snapshot']['project']['revision'] += 1
            atomic_json(self.path, state)
            return workspace
