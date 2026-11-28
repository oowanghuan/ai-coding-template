# Filesystem checkpoints and takeover checks

This module preserves explicit work directories. It does not own task state, run
Git, launch a model, resume a native Session, observe quota, or grant execution
rights. The scheduler calls it on concrete events (progress boundary, pause,
known stop, or handoff). No background watcher is implemented.

```python
from framework.recovery.checkpoint import create_snapshot, load_snapshot, restore_snapshot
from framework.recovery.admission import evaluate_takeover

receipt = create_snapshot(workspace, absent_checkpoint_directory, context, baseline_manifest)
manifest = load_snapshot(receipt['path'], receipt['manifest_sha256'])
decision = evaluate_takeover(manifest, trusted_current_observations, evaluation_time)
# The scheduler owns authority locking/recheck and any new assignment grant.
# Restoring bytes alone is also useful for inspection and grants no execution right.
restored = restore_snapshot(receipt['path'], receipt['manifest_sha256'], absent_destination)
```

Both destination parents must already exist. Source and destination must be
absolute, disjoint, explicit directories without symlink ancestors. A destination
must not exist, even if it is empty. Private sibling staging is published using
kernel atomic no-replace rename. Errors preserve source and uniquely named partial
staging for reconciliation; a partial staging tree is not a published checkpoint.
Existing destinations are never overwritten or merged. The implementation requires
macOS `renameatx_np(RENAME_EXCL)` or Linux `renameat2(RENAME_NOREPLACE)` and refuses
an unsafe fallback; only tested platforms may be claimed supported.

Context requires `wp_ref`, `assignment_ref`, positive `authority_epoch` and
`fencing_token`, `baseline_sha`, `last_valid_commit`, `completed`, `remaining`, and
`unknown_operations`. The latter uses existing protocol records
`{id, intent, reconciliation}` with unique IDs. Additional bounded JSON context
may carry role/authorization/spec/evidence references, decisions, blockers, next
actions and lease expiry; the scheduler remains responsible for those bindings.
Worker, tool provider, model provider and actual model remain separate references.
Optional authentication metadata contains protected credential references only,
never plaintext credentials. No supplier name or two-provider assumption appears
in the recovery protocol; a third synthetic adapter follows the same path.
Narrative and Git references are supplied observations, not authentication or a
claim this library inspected Git. Trusted scheduler input `baseline_manifest`
maps tracked paths to `{sha256, mode: "100644"|"100755"}`. Comparing bytes/modes
records tracked/untracked, dirty and deleted-tracked content. `.git` metadata is
excluded by default so a worktree pointer cannot expand the snapshot into other
repositories; an unsafe `.git` entry itself is still rejected. No other automatic
exclusions occur. Files ignored by Git are preserved as untracked content.

All regular content, executable flags and empty directories are preserved. The
module rejects symlinks, hardlinked files, sockets/FIFOs/devices, traversal and
unexpected checkpoint entries. It bounds files to 16 MiB each, 64 MiB total,
4096 files, 1024 directories and 4 MiB manifest. It does not preserve arbitrary
POSIX permissions, ACLs, xattrs or timestamps; restored data is private to the
operator, with executable flag retained. Pins must live outside candidate write
authority. Recomputed hashes next to a modified checkpoint are not trusted pins.

The scheduler should quiesce writers while checkpointing for coherent state.
Two complete reads plus file/directory identity/mtime/ctime comparisons reject
observed concurrent changes. This is not a filesystem snapshot primitive and
cannot freeze an uncontrolled writer after return. No repository authority is
modified and no assertion of a current Git ref is made.

`evaluate_takeover` accepts a validated manifest and these **trusted** current
observations: `wp_ref`, `old_assignment_ref`, `old_writer_status` (must be
`confirmed_stopped`), `old_fencing_token`, `authority_epoch`, distinct
`new_assignment_ref`, higher `new_fencing_token`, `new_lease_expires_at`,
`authorization_valid`, `budget_available`, `owner_status` (`active`),
`work_package_status` (`ready|paused`), and `reconciled_operations`. Each unresolved
operation needs `{outcome: confirmed_applied|confirmed_not_applied, evidence_ref}`.
Strings and model reports do not establish those facts; authoritative state and a
trusted observer do. Caller must recheck under the authority lock before granting
execution. Epoch migration is intentionally not accepted by this local protocol.
A decision always reports `execution_authorized: false`; it is an input to the
scheduler, not a new authority or substitute for fencing enforcement.
