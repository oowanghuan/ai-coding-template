"""Trusted local Store-to-invocation wiring; no model or provider-name branches.

This is supervisor code, not candidate code and not a CLI factory/sandbox. It
binds a prepared workspace to current authority and records an unresolved launch
in the SAME Store before any process can start. Exit alone never releases it.
"""
import copy

from framework.core.protocol import validate
from framework.local import lifecycle
from framework.local.handoff import binding
from framework.local.runner import verify_workspace
from framework.local.storage import authority_lock, atomic_json, fingerprint
from framework.local.store import Store, find, now, shape, DIRECT_WORKSPACE_PREFIX
from .invocation import LaunchReservations


class StoreBinding(LaunchReservations):
    """Use this SAME object as launch_reservations and its authorize callback.

    One object binds one Assignment, selection and prepared workspace. All pool
    bindings use the same protected reservation_root; the Store is authoritative.
    Fixed execution boundary must enforce scope before real CLI deployment.
    """
    def __init__(self, *, project_root, reservation_root, actor, authority, selection, cwd):
        super().__init__(reservation_root)
        self.store = Store(project_root)
        self.actor = actor
        if (type(authority) is not dict or set(authority) != {'assignment_id','workspace_id','epoch','token'} or
                any(type(authority[k]) is not int or authority[k] < 1 for k in ('epoch','token'))):
            raise ValueError('exact execution authority required')
        self.authority = copy.deepcopy(authority)
        self.selection = copy.deepcopy(selection)
        from framework.local.launch_driver import no_links
        self.cwd = no_links(cwd, directory=True)
        with authority_lock(self.store.root):
            state = self.store._read()
            assignment = find(state['snapshot']['assignments'], authority['assignment_id'])
            wp = find(state['snapshot']['work_packages'], assignment['wp_ref'])
            self.store_id = state['store_id']
            self.contract = binding(wp)
            self.authorization = fingerprint(find(state['snapshot']['authorizations'], wp['authorization_ref']))
            self.scope = dict(allowed_paths=copy.deepcopy(assignment['allowed_paths']),
                              forbidden_paths=copy.deepcopy(wp['forbidden_paths']))
        self._intent = None

    def _check(self, state, authority, proposal, *, fresh=False):
        if authority != self.authority or state['store_id'] != self.store_id:
            raise ValueError('Store/authority binding changed')
        observed = now()
        assignment, wp, worker = self.store._credential(state, authority, self.actor, observed, states=('active',))
        workspace = state['workspaces'][assignment['workspace_id']]
        if authority['workspace_id'] != workspace['id'] or workspace['id'].startswith(DIRECT_WORKSPACE_PREFIX):
            raise ValueError('workspace identity or execution domain mismatch')
        if workspace.get('recovery_source') and not workspace.get('restored'):
            raise ValueError('handoff restoration incomplete')
        if binding(wp) != self.contract or fingerprint(find(state['snapshot']['authorizations'], wp['authorization_ref'])) != self.authorization:
            raise ValueError('work contract or authorization changed; rebind after review')
        if assignment['allowed_paths'] != self.scope['allowed_paths']:
            raise ValueError('execution scope changed')
        if (proposal['assignment_id'] != assignment['id'] or proposal['work_package_id'] != wp['id'] or
                proposal['baseline_sha'] != assignment['base_sha'] or proposal['selection'] != self.selection):
            raise ValueError('proposal is not bound to the current work package')
        runtime = state.get('worker_runtime')
        if runtime is None: raise ValueError('verified Worker lifecycle required')
        member = runtime['workers'][worker['id']]
        provider = find(state['snapshot']['providers'], worker['provider_ref'])
        if (self.selection.get('adapter_id') != provider['adapter'] or
                self.selection.get('quota_group') != member['quota_group'] or
                any(self.selection.get(k) != member['resource'][k] for k in member['resource']) or
                not member['resource']['agent_tool'] or not member['resource']['model_provider']):
            raise ValueError('registered tool/provider/model/credential/quota selection mismatch')
        lifecycle.claimable(state, worker['id'], observed)
        errors = validate(state['snapshot'], observed)
        if errors: raise ValueError('; '.join(errors))
        prepared = workspace['state'] == 'prepared' and workspace['run'] is None
        own_intent = (not fresh and self._intent is not None and workspace['state'] == 'launching'
                      and workspace['run'] == self._intent)
        if not (prepared or own_intent): raise ValueError('workspace already launched or outcome unknown')
        if verify_workspace(self.store.root, workspace) != self.cwd:
            raise ValueError('fixed working directory differs from registered workspace')
        return assignment, workspace, worker

    def authorize(self, authority, proposal):
        with authority_lock(self.store.root):
            try: self._check(self.store._read(), authority, proposal)
            except (ValueError, KeyError): return False
        return True

    def runtime_authorize(self, record):
        if (self._intent is None or record['invocation_id'] != self._intent['invocation_id'] or
                record['binding_sha256'] != self._intent['binding_sha256']):
            return False
        proposal = dict(assignment_id=record['authority']['assignment_id'],
            work_package_id=record['work_package_id'], baseline_sha=record['baseline_sha'], selection=record['selection'])
        return self.authorize(record['authority'], proposal)

    def observe_terminal(self, record):
        """Record bounded process facts, even after fencing; never accept/release.

        Called by the trusted executor after checking protected output hashes.
        There is no public action accepting model-provided observations.
        """
        if record['state'] not in ('exited','stopped','timed_out','output_limited','outcome_unknown'):
            raise ValueError('process is not terminal')
        if (record['authority'] != self.authority or record['selection'] != self.selection or
                record.get('writer_stop_confirmed') is not False or record.get('engineering_accepted') is not False):
            raise ValueError('invalid terminal authority/acceptance assertion')
        observation = {key: copy.deepcopy(record.get(key)) for key in
            ('invocation_id','binding_sha256','intent_sha256','state','exit_code','stdout_sha256',
             'stderr_sha256','stop_reason','authority_watch')}
        with authority_lock(self.store.root):
            state = self.store._read()
            if state['store_id'] != self.store_id: raise ValueError('Store identity changed')
            workspace = state['workspaces'][self.authority['workspace_id']]
            run = workspace['run']
            if (run is None or run.get('format') != 'provider-launch-intent/1' or
                    any(run.get(k) != record[k] for k in ('invocation_id','binding_sha256','intent_sha256','authority','selection'))):
                raise ValueError('terminal observation does not match Store launch intent')
            previous = run.get('process_observation')
            result = dict(invocation_id=record['invocation_id'], observed=True,
                          writer_stop_confirmed=False, engineering_accepted=False, workspace_state=workspace['state'])
            if previous is not None:
                if previous != observation: raise ValueError('conflicting terminal observation')
                return result  # No revision increment or new side effect on retry.
            if workspace['state'] not in ('launching','running','unknown'):
                raise ValueError('workspace already reconciled by another trusted path')
            run['process_observation'] = observation
            workspace['state'] = 'unknown'  # Main-process exit is not writer-stop proof.
            result['workspace_state'] = 'unknown'
            state['revision'] += 1
            state['snapshot']['project']['revision'] += 1
            key = 'provider-observed:' + record['invocation_id']
            if key in state['operations']: raise ValueError('observation operation already recorded')
            state['operations'][key] = dict(intent=fingerprint(observation), action='provider-process-observed',
                actor=self.actor, at=now(), status='committed', result=result, revision=state['revision'])
            shape(state)
            atomic_json(self.store.path, state)
            return result

    def reserve(self, record, *, cwd, journal_root):
        if cwd != self.cwd or record['selection'] != self.selection:
            raise ValueError('fixed invocation binding changed')
        proposal = dict(assignment_id=record['authority']['assignment_id'],
            work_package_id=record['work_package_id'], baseline_sha=record['baseline_sha'], selection=record['selection'])
        with authority_lock(self.store.root):
            state = self.store._read()
            _, workspace, worker = self._check(state, record['authority'], proposal, fresh=True)
            intent = dict(format='provider-launch-intent/1', state='launching',
                invocation_id=record['invocation_id'], binding_sha256=record['binding_sha256'],
                intent_sha256=record['intent_sha256'], stdin_sha256=record['stdin_sha256'],
                authority=copy.deepcopy(record['authority']), selection=copy.deepcopy(self.selection),
                contract_sha256=self.contract, authorization_sha256=self.authorization,
                writer_stop_confirmed=False, started_at=now())
            workspace.update(state='launching', run=intent)
            state['worker_runtime']['workers'][worker['id']]['stop_confirmed'] = False
            state['revision'] += 1
            state['snapshot']['project']['revision'] += 1
            key = 'provider-start:' + record['invocation_id']
            if key in state['operations']: raise ValueError('launch operation already recorded')
            state['operations'][key] = dict(intent=fingerprint(intent), action='provider-run-begin',
                actor=self.actor, at=now(), status='committed', result=copy.deepcopy(intent), revision=state['revision'])
            shape(state)
            atomic_json(self.store.path, state)
        # Store first: any failure/lost receipt after its commit stays unresolved.
        # Never roll back a reservation or issue a new permission on replay.
        super().reserve(record, cwd=cwd, journal_root=journal_root)
        self._intent = intent
