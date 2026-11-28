"""Trusted single-host checkpoint and handoff integration; no provider-name branches.

Pins and observations live in the same local authority. This is not remote worker
authentication. Actual stop must be observed through an owned process handle.
"""
import copy
import hashlib
import os
from pathlib import Path
import uuid

from framework.local.storage import authority_lock, atomic_json, fingerprint, safe_path
from framework.local.store import Store, find, now, shape, UNKNOWN, LAUNCH_PROTOCOL, DIRECT_WORKSPACE_PREFIX
from framework.local import lifecycle
from framework.local.runner import git, workspace_entries, prepare, verify_workspace
from framework.core.protocol import validate, within, timestamp
from framework.recovery.checkpoint import create_snapshot, load_snapshot, restore_snapshot, open_directory, scan


def binding(wp):
    return fingerprint({key: wp[key] for key in ('baseline_sha', 'spec_refs', 'allowed_paths',
        'forbidden_paths', 'authorization_ref', 'risk', 'accountable_role', 'external_effects')})


def commit(store, state, action, result):
    state['revision'] += 1
    state['snapshot']['project']['revision'] += 1
    operation_id = action + ':' + uuid.uuid4().hex
    state['operations'][operation_id] = dict(intent=fingerprint(result), action=action,
        actor='trusted-local-supervisor', at=now(), status='committed', result=result, revision=state['revision'])
    errors = validate(state['snapshot'], now())
    if errors:
        raise ValueError('; '.join(errors))
    shape(state)
    atomic_json(store.path, state)
    return result


def assigned(state, credentials, actor):
    if type(credentials['token']) is not int or type(credentials['epoch']) is not int:
        raise ValueError('epoch/token must be integers')
    assignment = find(state['snapshot']['assignments'], credentials['assignment_id'])
    worker = find(state['snapshot']['workers'], assignment['worker_ref'])
    wp = find(state['snapshot']['work_packages'], assignment['wp_ref'])
    if (actor != worker['principal'] or credentials['token'] != assignment['fencing_token'] or
        credentials['epoch'] != assignment['authority_epoch'] or
        assignment['authority_epoch'] != state['snapshot']['project']['authority_epoch'] or
        wp['assignment_ref'] != assignment['id']):
        raise ValueError('handoff ownership binding changed')
    return assignment, worker, wp, state['workspaces'][assignment['workspace_id']]


def checkpoint(root, credentials, actor, *, completed=(), remaining=(), evidence_refs=()):
    store = Store(root)
    with authority_lock(store.root):
        state = store._read()
        receipt = capture_checkpoint_state(store, state, credentials, actor, completed=completed,
                                           remaining=remaining, evidence_refs=evidence_refs)
        return commit(store, state, 'checkpoint', receipt)


def capture_checkpoint_state(store, state, credentials, actor, *, completed=(), remaining=(), evidence_refs=()):
    """Internal transaction helper: caller holds Store lock and commits state.

    Published snapshot artifacts may survive a failed state commit; never delete
    or overwrite them on retry. A snapshot is not stopped-writer proof.
    """
    assignment, worker, wp, workspace = assigned(state, credentials, actor)
    source = safe_path(store.root, workspace['path'])
    verify_workspace(store.root, workspace)
    baseline = {path: {'sha256': hashlib.sha256(git(store.root, 'cat-file', 'blob', blob)).hexdigest(),
                       'mode': mode} for mode, blob, path in workspace_entries(store.root, assignment['base_sha'])}
    cp_id = 'checkpoint-' + uuid.uuid4().hex
    context = dict(wp_ref=wp['id'], assignment_ref=assignment['id'],
        authority_epoch=assignment['authority_epoch'], fencing_token=assignment['fencing_token'],
        baseline_sha=assignment['base_sha'], last_valid_commit=git(source, 'rev-parse', 'HEAD').decode().strip(),
        completed=list(completed), remaining=list(remaining),
        unknown_operations=copy.deepcopy((workspace['run'] or {}).get('unknown_operations', [])),
        spec_refs=wp['spec_refs'], authorization_ref=wp['authorization_ref'],
        role_ref=assignment['role_ref'], evidence_refs=list(evidence_refs),
        lease_expires_at=assignment['lease_expires_at'], binding=binding(wp))
    parent = safe_path(store.root, '.ai-org/checkpoints')
    parent.mkdir(mode=0o700, exist_ok=True)
    receipt = create_snapshot(source, parent / cp_id, context, baseline)
    record = dict(path='.ai-org/checkpoints/' + cp_id, manifest_sha256=receipt['manifest_sha256'],
                  binding=binding(wp), unknown_digest=fingerprint(context['unknown_operations']))
    workspace['checkpoint'] = record
    cp = dict(id=cp_id, wp_ref=wp['id'], wp_revision=wp['revision'], role_ref=assignment['role_ref'],
        authorization_ref=wp['authorization_ref'], assignment_ref=assignment['id'],
        lease_expires_at=assignment['lease_expires_at'], created_at=now(), spec_refs=wp['spec_refs'],
        baseline_sha=assignment['base_sha'], last_valid_commit=context['last_valid_commit'],
        uncommitted=[{'location': record['path'], 'sha256': record['manifest_sha256']}],
        completed=list(completed), remaining=list(remaining), evidence_refs=list(evidence_refs),
        decision_refs=[], blockers=[], unknown_operations=context['unknown_operations'],
        next_actions=['Reconcile exact current authority and stopped writer before handoff'])
    state['snapshot']['checkpoints'].append(cp)
    assignment['last_checkpoint'] = cp_id
    wp['checkpoint_ref'] = cp_id
    return dict(checkpoint_id=cp_id, **record)


def confirm_stopped(root, credentials, actor, process):
    """Accept an owned Popen after wait; never an untrusted JSON 'stopped' flag.

    The reviewed launcher must have used start_new_session and a policy denying
    process escape. A live process group is unresolved even if its leader exited.
    A snapshot taken before exit is provisional: final workspace bytes must still
    match, otherwise preserve them and checkpoint again after the actual stop.
    """
    status = process.poll()
    if status is None:
        raise ValueError('writer still running')
    process.wait(timeout=0)
    try:
        os.killpg(process.pid, 0)
    except ProcessLookupError:
        pass
    else:
        raise ValueError('process group still has writers')
    store = Store(root)
    with authority_lock(store.root):
        state = store._read()
        assignment, worker, wp, workspace = assigned(state, credentials, actor)
        run = workspace['run'] or {}
        if run.get('pid') != process.pid or run.get('process_group') != process.pid:
            raise ValueError('owned process is not registered execution')
        if not workspace.get('checkpoint'):
            raise ValueError('preserve checkpoint before releasing unknown execution')
        checked_checkpoint(store.root, state, wp, workspace)
        workspace['state'] = 'stopped'
        workspace['run'] = dict(run, state='stopped', exit_code=status)
        if 'worker_runtime' in state:
            others = any(w['state'] in UNKNOWN and
                         find(state['snapshot']['assignments'], w['assignment_id'])['worker_ref'] == worker['id']
                         for w in state['workspaces'].values())
            state['worker_runtime']['workers'][worker['id']]['stop_confirmed'] = not others
            lifecycle.refresh(state, worker['id'])
        return commit(store, state, 'confirmed-stop', {'assignment_id': assignment['id'], 'exit_code': status})


def recover_prepared(root, credentials, actor, expected_revision, operation_id):
    """Fence an exactly checkpointed workspace with durable no-launch proof.

    This is limited to cooperative reviewed launchers obeying the versioned
    persist-before-spawn protocol. It is not an OS process-absence detector.
    Only a direct-local-only claim uses the reserved workspace namespace. The
    reviewed external client and driver reject that namespace, including target
    paths beneath an ancestor job. Existing pinned legacy drivers must not have
    authority over the new namespace. Out-of-band writers or unknown external
    authority require separate reconciliation; they are not supported here.
    The caller first saves a final checkpoint. Same operation/intent replays the
    committed receipt without writes; a new operation cannot recover it twice.
    Legacy prepared workspaces without versioned history fail closed.
    """
    return Store(root).change('recover-prepared', credentials, actor,
                              expected_revision, operation_id)


def recover_prepared_state(root, state, credentials, actor, at):
    """Internal Store transaction; caller holds the one authority lock."""
    assignment, worker, wp, workspace = assigned(state, credentials, actor)
    if (not workspace['id'].startswith(DIRECT_WORKSPACE_PREFIX) or
            workspace['path'] != '.ai-org/workspaces/' + workspace['id']):
        raise ValueError('prepared recovery requires the direct-local-only execution domain')
    if (assignment['state'] not in ('active', 'revoked', 'expired') or
            workspace['state'] != 'prepared' or workspace['run'] is not None):
        raise ValueError('prepared recovery requires an unlaunched current assignment')
    if wp['id'] in state['deliveries']:
        raise ValueError('delivered work cannot use prepared recovery')
    if (not workspace.get('checkpoint') or not assignment['last_checkpoint'] or
            wp['checkpoint_ref'] != assignment['last_checkpoint']):
        raise ValueError('final current checkpoint required before prepared recovery')
    auth = find(state['snapshot']['authorizations'], wp['authorization_ref'])
    if auth['state'] != 'granted' or timestamp(auth['expires_at']) <= timestamp(at):
        raise ValueError('authorization changed or expired; preserve for explicit reconciliation')
    expected = dict(workspace_id=workspace['id'], state='creating', launch_protocol=LAUNCH_PROTOCOL,
        execution_domain='direct-local-only',
        assignment_id=assignment['id'], epoch=assignment['authority_epoch'], token=assignment['fencing_token'],
        work_binding_sha256=binding(wp),
        authorization_sha256=fingerprint(auth))
    starts = []
    checkpoints = []
    for record in state['operations'].values():
        result = record['result']
        if record['action'] == 'run-begin':
            # An unusable launch history is unknown, not evidence of absence.
            if not isinstance(result.get('workspace_id'), str):
                raise ValueError('unverifiable launch history')
            if result['workspace_id'] == workspace['id']:
                raise ValueError('persistent launch intent exists; reconcile owned execution')
        if record['action'] == 'start' and result.get('workspace_id') == workspace['id']:
            starts.append(record)
        if record['action'] == 'checkpoint' and result.get('checkpoint_id') == assignment['last_checkpoint']:
            checkpoints.append(record)
    if (len(starts) != 1 or starts[0]['status'] != 'committed' or starts[0]['actor'] != actor or
            starts[0]['result'] != expected or
            type(starts[0]['result'].get('epoch')) is not int or
            type(starts[0]['result'].get('token')) is not int):
        raise ValueError('missing or ambiguous versioned launch-protocol proof')
    if (len(checkpoints) != 1 or checkpoints[0]['status'] != 'committed' or
            checkpoints[0]['revision'] <= starts[0]['revision'] or
            checkpoints[0]['result'] != dict(checkpoint_id=assignment['last_checkpoint'], **workspace['checkpoint'])):
        raise ValueError('final checkpoint history is not bound to preparation')
    checked_checkpoint(root, state, wp, workspace)
    # The same lock protects run-begin. If launch won the race, checks above
    # reject. If recovery wins, these credentials cannot authorize a later
    # launch. No PID absence or caller-supplied stopped boolean is consulted.
    if assignment['state'] == 'active':
        assignment.update(state='revoked', revocation_reason='prepared-checkpoint-recovery')
    wp.update(state='paused', revision=wp['revision'] + 1)
    workspace.update(state='stopped', handoff_required=True)
    if 'worker_runtime' in state:
        unresolved = any(w['state'] in UNKNOWN and
            find(state['snapshot']['assignments'], w['assignment_id'])['worker_ref'] == worker['id']
            for w in state['workspaces'].values())
        state['worker_runtime']['workers'][worker['id']]['stop_confirmed'] = not unresolved
        lifecycle.refresh(state, worker['id'])
    return dict(assignment_id=assignment['id'], workspace_id=workspace['id'], state='stopped',
        execution_observed='never_launched', process_stop_observed=False, launch_protocol=LAUNCH_PROTOCOL,
        checkpoint_id=assignment['last_checkpoint'], manifest_sha256=workspace['checkpoint']['manifest_sha256'])


def checked_checkpoint(root, state, wp, workspace):
    record = workspace['checkpoint']
    if record['binding'] != binding(wp):
        raise ValueError('baseline/spec/scope changed since checkpoint')
    if record['unknown_digest'] != fingerprint((workspace['run'] or {}).get('unknown_operations', [])):
        raise ValueError('new unknown operation since checkpoint')
    manifest = load_snapshot(safe_path(root, record['path']), record['manifest_sha256'])
    context = manifest['context']
    old = find(state['snapshot']['assignments'], workspace['assignment_id'])
    latest = find(state['snapshot']['checkpoints'], old['last_checkpoint'])
    if (context['assignment_ref'] != old['id'] or context['wp_ref'] != wp['id'] or
        context['fencing_token'] != old['fencing_token'] or context['authority_epoch'] != old['authority_epoch'] or
        latest['uncommitted'] != [{'location': record['path'], 'sha256': record['manifest_sha256']}]):
        raise ValueError('latest checkpoint/assignment pin mismatch')
    if context['unknown_operations']:
        raise ValueError('unknown operations require reconciliation before handoff')
    check_workspace_snapshot(root, workspace, manifest)
    return manifest


def check_workspace_snapshot(root, workspace, manifest):
    """Validate stopped-writer content, not merely a still-valid snapshot pin.

    The authority lock serializes supervisor state, not filesystem writes. The
    supervisor must keep the stopped workspace without other authorized writers;
    same-account hostile concurrent writes are outside this single-host contract.
    Recheck at stop, claim and before/after restore to reject observed late changes.
    Git administrative metadata is excluded as in create_snapshot; HEAD remains
    bound and no path/link/type validation is relaxed for a stopped workspace.
    """
    source = verify_workspace(root, workspace)
    head = git(source, 'rev-parse', 'HEAD').decode().strip()
    if head != manifest['context']['last_valid_commit']:
        raise ValueError('workspace HEAD differs from checkpoint; preserve and create final checkpoint')
    fd = open_directory(source)
    try:
        first = scan(fd, exclude_git=manifest['excluded_git_metadata'])
        second = scan(fd, exclude_git=manifest['excluded_git_metadata'])
    finally:
        os.close(fd)
    expected = {name: {key: entry[key] for key in ('sha256', 'size', 'mode')}
                for name, entry in manifest['files'].items()}
    if (first != second or first[0] != expected or first[1] != manifest['directories']):
        raise ValueError('workspace differs from checkpoint; preserve and create final checkpoint after stop')
    # Also reject a swapped root/HEAD during the scan, without following links.
    current = verify_workspace(root, workspace)
    current_fd = open_directory(current)
    try:
        if scan(current_fd, exclude_git=manifest['excluded_git_metadata']) != second:
            raise ValueError('workspace changed while validating final checkpoint')
    finally:
        os.close(current_fd)
    if git(current, 'rev-parse', 'HEAD').decode().strip() != head:
        raise ValueError('workspace HEAD changed while validating final checkpoint')


def prepare_handoff(root, credentials, actor, expected_revision, operation_id):
    """Restore into a fresh registered worktree; never overwrite the old workspace."""
    store = Store(root)
    before = store.inspect()['state']
    new = find(before['snapshot']['assignments'], credentials['assignment_id'])
    target = before['workspaces'][new['workspace_id']]
    if not target.get('recovery_source'):
        return prepare(root, credentials, actor, expected_revision, operation_id)
    # Persist execution intent first, then keep state locked through content restore.
    result = prepare(root, credentials, actor, expected_revision, operation_id)
    with authority_lock(store.root):
        state = store._read()
        new, wp, worker = store._credential(state, credentials, actor, now(), states=('active',))
        target = state['workspaces'][new['workspace_id']]
        if target.get('restored'):
            return result
        target['state'] = 'creating'
        commit(store, state, 'restore-intent', {'assignment_id': new['id'], 'source': target['recovery_source']})
        old_workspace = state['workspaces'][target['recovery_source']]
        if old_workspace['state'] != 'stopped':
            raise ValueError('old writer stop unconfirmed')
        manifest = checked_checkpoint(store.root, state, wp, old_workspace)
        source = old_workspace['checkpoint']
        artifact = safe_path(store.root, '.ai-org/checkpoints/restore-' + uuid.uuid4().hex)
        restore_snapshot(safe_path(store.root, source['path']), source['manifest_sha256'], artifact)
        dest = verify_workspace(store.root, target, pristine=True)
        # Only changed assigned files may be restored. Validate all changes before writing.
        baseline = {path: (mode, git(store.root, 'cat-file', 'blob', blob))
                    for mode, blob, path in workspace_entries(store.root, new['base_sha'])}
        files = {str(p.relative_to(artifact)): p for p in artifact.rglob('*') if p.is_file()}
        edits = []
        for relative in sorted(set(baseline) | set(files)):
            item = files.get(relative)
            content = item.read_bytes() if item else None
            mode = '100755' if item and item.stat().st_mode & 0o111 else '100644'
            if baseline.get(relative) == (mode, content):
                continue
            if (not any(within(relative, p) for p in new['allowed_paths']) or
                any(within(relative, p) for p in wp['forbidden_paths'])):
                raise ValueError('checkpoint modifications exceed new scope')
            edits.append((relative, content, mode))
        for relative, content, mode in edits:
            path = safe_path(dest, relative)
            if content is None:
                path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                path.chmod(0o700 if mode == '100755' else 0o600)
        # A late old-workspace change must never turn the persisted creating
        # intent into an executable prepared handoff, even if restore succeeded.
        checked_checkpoint(store.root, state, wp, old_workspace)
        target['restored'] = {'manifest_sha256': source['manifest_sha256'], 'changed_paths': [e[0] for e in edits]}
        target['state'] = 'prepared'
        commit(store, state, 'restore-handoff', dict(assignment_id=new['id'], **target['restored']))
    return result
