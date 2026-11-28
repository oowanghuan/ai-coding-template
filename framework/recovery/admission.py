"""Pure takeover checks on trusted scheduler observations, never model assertions.

The scheduler must read current authority under its lock, observe actual stop,
validate the checkpoint pin, and recheck before granting a new assignment. This
function does not acquire that lock, stop a process, or authenticate observations.
"""
from datetime import datetime, timezone

from .checkpoint import context_valid


def timestamp(value):
    return datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def evaluate_takeover(checkpoint, current, at):
    """Return a decision only, with no filesystem or task-state mutation.

    checkpoint is a manifest already loaded with its pinned hash. Current values
    must be supplied by the authoritative scheduler and trusted process observer.
    A successful decision is neither a lease nor a proof of stopped execution.
    """
    reasons = []
    try:
        context = checkpoint['context']; context_valid(context); moment = timestamp(at)
        if current['wp_ref'] != context['wp_ref']: reasons.append('work-package-mismatch')
        if current['old_assignment_ref'] != context['assignment_ref']: reasons.append('old-assignment-mismatch')
        if current['old_writer_status'] != 'confirmed_stopped': reasons.append('old-writer-not-confirmed-stopped')
        if type(current['old_fencing_token']) is not int or current['old_fencing_token'] != context['fencing_token']: reasons.append('old-fence-mismatch')
        if type(current['authority_epoch']) is not int or current['authority_epoch'] != context['authority_epoch']:
            reasons.append('authority-epoch-mismatch')
        token = current['new_fencing_token']
        if type(token) is not int or token <= context['fencing_token']: reasons.append('new-fence-not-higher')
        if not isinstance(current['new_assignment_ref'],str) or not current['new_assignment_ref'] or current['new_assignment_ref']==context['assignment_ref']:
            reasons.append('new-assignment-required')
        if current['authorization_valid'] is not True: reasons.append('authorization-not-valid')
        if current['budget_available'] is not True: reasons.append('budget-not-available')
        if current['owner_status'] != 'active': reasons.append('owner-not-active')
        if current['work_package_status'] not in ('ready','paused'): reasons.append('task-not-recoverable')
        if timestamp(current['new_lease_expires_at']) <= moment: reasons.append('new-lease-expired')
        reconciled = current['reconciled_operations']
        if not isinstance(reconciled,dict): raise ValueError('invalid reconciliation map')
        for operation in context['unknown_operations']:
            item = reconciled.get(operation['id'])
            if (not isinstance(item,dict) or item.get('outcome') not in ('confirmed_applied','confirmed_not_applied')
                    or not isinstance(item.get('evidence_ref'),str) or not item['evidence_ref'].strip()):
                reasons.append('unknown-operation-unreconciled:' + operation['id'])
    except (KeyError, TypeError, ValueError, OverflowError):
        reasons.append('invalid-or-missing-authority-observation')
    return {'format':'recovery-admission/1','admissible':not reasons,'reasons':sorted(set(reasons)),
            'execution_authorized':False, 'observation_source':'trusted_scheduler_required',
            'requires_atomic_authority_recheck':True}
