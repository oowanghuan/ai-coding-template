"""Trusted invocation-to-checkpoint preservation; never grants writer handoff."""
import copy

from framework.local import handoff, lifecycle
from framework.local.storage import authority_lock, fingerprint, safe_path
from framework.recovery.checkpoint import load_snapshot
from .runspec import ID
from .store_binding import StoreBinding


def preserve_invocation(executor, invocation_id, *, operation_id, completed=(), remaining=(), evidence_refs=()):
    """Preserve actual workspace with an explicit unresolved provider operation.

    Reads protected invocation state, not a model-provided terminal report.
    Even an observed main-process exit is provisional for recovery. No PID stop,
    release, native resume, output application or delivery occurs here.
    """
    bridge = executor.reservations
    if not isinstance(bridge, StoreBinding): raise ValueError('Store-bound preservation required')
    if not isinstance(operation_id, str) or not ID.fullmatch(operation_id): raise ValueError('operation identity')
    narratives = {}
    for name, values in [('completed', completed), ('remaining', remaining), ('evidence_refs', evidence_refs)]:
        if (not isinstance(values, (tuple, list)) or len(values) > 64 or
                any(not isinstance(v, str) or not v.strip() or len(v.encode()) > 4096 for v in values)):
            raise ValueError('bounded checkpoint narrative required')
        narratives[name] = list(values)
    record = executor.status(invocation_id=invocation_id)
    if record['state'] not in ('exited','stopped','timed_out','output_limited','outcome_unknown'):
        raise ValueError('running invocation requires stop/reconciliation before terminal preservation')
    if record['stdout_sha256'] is not None or record['stderr_sha256'] is not None:
        # Missing/modified captured output cannot be silently downgraded to a
        # result-free preservation. result verifies hashes and writes observation.
        executor.result(invocation_id=invocation_id)
    else:
        # Supervision/launch failure may have no complete result; record only
        # the protected unknown observation, never fabricate output evidence.
        bridge.observe_terminal(record)
    intent = fingerprint(dict(invocation_id=invocation_id, binding_sha256=record['binding_sha256'],
                              intent_sha256=record['intent_sha256'], **narratives))
    with authority_lock(bridge.store.root):
        state = bridge.store._read()
        assignment, worker, wp, workspace = handoff.assigned(state, bridge.authority, bridge.actor)
        if (state['store_id'] != bridge.store_id or workspace['id'] != bridge.authority['workspace_id'] or
                handoff.binding(wp) != bridge.contract):
            raise ValueError('preservation authority/contract changed; reconcile first')
        run = workspace['run'] or {}
        if (run.get('format') != 'provider-launch-intent/1' or
                any(run.get(k) != record[k] for k in ('invocation_id','binding_sha256','intent_sha256','authority','selection'))):
            raise ValueError('preservation does not match registered launch')
        if workspace['state'] != 'unknown': raise ValueError('workspace already reconciled by another path')
        if assignment['state'] not in ('active','revoked','expired') or wp['state'] not in ('in_progress','paused'):
            raise ValueError('task is not eligible for unresolved invocation preservation')
        saved = run.get('preservations', {}).get(operation_id)
        if saved is not None:
            if saved['intent'] != intent: raise ValueError('preservation operation reused for changed intent')
            result = copy.deepcopy(saved['result'])
            manifest = load_snapshot(safe_path(bridge.store.root, result['path']), result['manifest_sha256'])
            handoff.check_workspace_snapshot(bridge.store.root, workspace, manifest)
            return result  # Verify actual bytes; no state revision or new snapshot.
        unknown = copy.deepcopy(run.get('unknown_operations', []))
        operation = dict(id='provider-' + invocation_id,
            intent='Reconcile provider execution and all writer stop: ' + record['intent_sha256'],
            reconciliation='Main process observation is insufficient; retain original launch, captured evidence and workspace until trusted full-writer and external-effect reconciliation.')
        existing = [x for x in unknown if x['id'] == operation['id']]
        if existing and existing != [operation]: raise ValueError('unknown operation identity conflict')
        if not existing: unknown.append(operation)
        run['unknown_operations'] = unknown
        # A current checkpoint with unknown operations cannot remain on an
        # in-progress task. Fence this Assignment only, in the same commit as
        # its checkpoint and receipt; do not pause unrelated work/quota groups.
        if assignment['state'] == 'active':
            assignment.update(state='revoked', revocation_reason='provider invocation requires recovery reconciliation')
        if wp['state'] != 'paused': wp.update(state='paused', revision=wp['revision'] + 1)
        workspace['handoff_required'] = True
        if 'worker_runtime' in state:
            state['worker_runtime']['workers'][worker['id']]['stop_confirmed'] = False
            lifecycle.refresh(state, worker['id'])
        receipt = handoff.capture_checkpoint_state(bridge.store, state, bridge.authority, bridge.actor, **narratives)
        result = dict(format='provider-preservation/1', selection=copy.deepcopy(record['selection']),
            invocation_id=invocation_id, operation_id=operation_id, **receipt,
            provisional=True, writer_stop_confirmed=False, recovery_ready=False, engineering_accepted=False)
        run.setdefault('preservations', {})[operation_id] = dict(intent=intent, result=copy.deepcopy(result))
        return handoff.commit(bridge.store, state, 'provider-checkpoint', result)
