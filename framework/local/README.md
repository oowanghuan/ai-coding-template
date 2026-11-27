# Local execution preview — WP-102 / WP-103

This is a single-host controller for cooperating workers of one OS owner. It is
not a distributed lock service, provider adapter, cryptographic identity service
or engineering acceptance Gate. The controller must be reviewed/trusted; actor
IDs are assertions supplied by that controller, not authentication tokens.
Never execute an unreviewed checkout with publication credentials.

## Authority and protocol changes

`.ai-org/state.json` is the only task authority: protocol snapshot, store ID,
monotonic revision, fencing counters, operation receipts, workspaces and captured
deliveries commit together through one locked, fsynced atomic replacement.
`.ai-org/install-journal.json` and `installations/` govern file installation only.
They cannot grant task rights. An unresolved installation blocks controller writes.

Protocol 0.2 adds `reserved` assignments (task `ready`) before actual start
(`active` / `in_progress`). Empty projects can have no providers/hosts and a null
baseline while planned. Protocol 0.1 retains its previous shape restrictions.
`init` explicitly imports into the versioned local envelope and refuses live claims
or a different backend. It never silently overwrites an existing authority.

All mutations carry operation ID and expected revision. One lock serializes
dependency, authorization, resource and scope checks with allocation. Same ID and
intent returns the historical receipt; different intent is an error. A replay is
not a renewed lease. Start/run/submit check fresh epoch, token and lease separately.
Replaying a failed finished process remains a CLI failure; its original exit code,
PID and log fingerprints are retained without another launch or delivery.
Reclaiming a stopped/released workspace allocates a new token and new directory.

This initial API deliberately has no generic JSON overwrite endpoint. Import an
explicitly reviewed snapshot, then register/claim/start/heartbeat/release/revoke.
Changing live task definitions or authorizations needs a reviewed migration, not
hand edits to the aggregate. Full PMO/task editing and provider adapters are later
packages. An installed bootstrap project is therefore not automatically runnable.

## Execution and recovery

The only runnable adapter is a bounded synthetic writer (no arbitrary command,
network, model, login or paid API). It creates a detached worktree without checkout
hooks or filters, materializes regular Git blobs, then checks the baseline/index.
Symlinks, submodules and reserved state paths in the baseline are refused.

Before worktree creation or process launch, the controller persists intent. A
missing response does not permit blind replay. A complete pre-launch worktree can
be reconciled by verifying registration, HEAD, index and every baseline file.
Partial/modified materializations and unknown running processes remain preserved
and block reassignment. There is no automatic kill-by-stale-PID or reboot inference.
The current automatic reconciler handles only complete pre-launch worktrees;
unknown process recovery still requires external inspection. Do not claim full
crash/takeover acceptance from this preview.

The macOS worker sandbox permits writing only the selected output and scratch,
with no credentials, network, controller state or unrelated host files. Unsupported
OS or failed sandbox initialization fails closed; there is no unsandboxed fallback.
The tested macOS host rejects nested Seatbelt initialization. Inside that outer
Seatbelt harness, the default `run` backend retains three skipped checks: its
single-task success chain, dual-task success chain and inner policy probe. Its
failure-closed tests must pass. Standalone worker/policy checks and controller
tests are separate evidence, not a substitute for a full integration run.

Fencing protects the controller and captured delivery. It does not assert that an
expired process has ceased writing its old directory. Captured files are bounded,
hashed, stored as bytes in the authority and returned with `accepted: false`.
No test report, review milestone, merge or business acceptance is inferred.

## Explicit external launcher

`run-external` is an optional finite-batch backend for the same fixed synthetic
writer. The existing `run` command keeps its direct-launch behavior. The external
controller and Worker run in separate sandboxes; an independently reviewed,
hash-pinned launcher starts the Worker as a sibling process. This avoids nesting
without removing the controller's outer protection. It adds no model, provider
session, network, credentials, arbitrary command option or persistent service.

Deployment has two distinct roots. **C** is the controller's sole writable fixture
tree, containing its project/worktrees and request mailbox. **T** contains the
reviewed launcher and fixed Worker copies, their hashes, batch configuration,
receipts and per-job scratch/logs. C and T must not contain each other. The outer
controller may read the required T configuration and receipts/logs but cannot
write T. Each Worker may write only its own scratch and configured output; it
cannot modify launcher configuration, receipts or another job's scratch.

The outer policy must protect the C root itself against removal, rename and
replacement, including an explicit rule using its actual canonical path:

```scheme
(deny file-write-unlink (literal "<C>"))
```

This is a required restriction within a complete deny-default profile, not a
standalone sandbox. A non-writable parent or string comparison of paths is
insufficient. Before execution, real canaries must confirm C cannot be replaced
with a symlink, output-ancestor replacement cannot escape C, and a hardlink alias
cannot make a protected T file writable through C. Network, credentials, checkout
and unrelated host access must remain denied. The fixed Worker's output rule
requires both the C anchor and its configured literal output path; it does not
grant workspace reads. Pure policy-string tests do not establish these protections.

First perform normal authorization, claim and Worktree preparation within the
outer sandbox, including the fixed output's parent directories. A trusted
coordinator then provisions the protected configuration for one or two jobs. Each
job binds its ID, operation ID, actual workspace, output path, content hash and
time bounds. No duplicate or nested workspaces are allowed. Configuration and
program bytes are fixed before the finite launcher runs:

```sh
# Trusted host operation: only the independently reviewed, hash-pinned T copy.
/usr/bin/python3 -I -B -S '<T>/launch_driver.py' --config '<T>/config.json'
```

Use a separate invocation inside the enforced controller sandbox to submit the
prepared job through the actual CLI:

```sh
# Run this invocation inside the configured outer sandbox, not directly on the host.
python3 '<FRAMEWORK_ROOT>/scripts/v4_local.py' run-external \
  --root '<C>/project' --actor 'principal-implementer' \
  --input '<C>/run-input.json' --expected-revision '<current-revision>' \
  --operation-id 'run-a' --launcher-config '<T>/config.json' \
  --launcher-job-id 'job-a'
```

These are invocation templates; replace placeholders using the reviewed fixture
and isolation policy. Input has `credentials`, `path`, `content` and optional
`delay_seconds`/`timeout`; all must match the protected job configuration. An
installed bootstrap project does not automatically provision jobs or execution
rights. The driver generates its own policy and fixed argv/environment; requests
cannot supply commands, environment variables or sandbox permissions.

The controller persists launch intent and checks fresh execution rights. Requests
are immutable, and receipts bind the job, operation, request hash, exact config
file hash and monotonic sequence. Receipts describe process effects; project task
authority remains solely in `.ai-org/state.json`. A successful execution still
requires a separate fresh-credential `submit` to capture delivery.

The launcher supervises only its own live child processes, with nonblocking stdin
and bounded runtime. Sending cancel is not proof of stopping: `stopped` requires
an observed exit and preserved log fingerprints. A confirmed prelaunch rejection
is distinct and has no PID/exit claim. Missing receipts, unconfirmed cancellation
or a restarted launch intent remain unknown and cannot authorize replay or a new
writer. Persisted PIDs never authorize killing an unrelated process.

External-backend evidence must identify the exact driver, Worker, controller,
configuration and real execution path. Fake subprocess tests cover interface
behavior only. An external success must not turn the direct backend's three
skipped checks into passes, and two process IDs alone do not establish overlapping
Worker task execution. This description does not assert successful integration
or acceptance; consult the evidence for the exact tested revision.

## Project installation

The installer copies neutral project assets, not the CLI or its Python dependencies.
Keep a reviewed framework checkout with the pinned dependencies available.
`FRAMEWORK_ROOT` is that checkout; `TARGET_ROOT` is the project being managed.
Use absolute, canonical paths and the required execution isolation for that
reviewed controller. Commands work from either directory:

```sh
FRAMEWORK_ROOT='/absolute/path/to/reviewed-framework'
TARGET_ROOT='/private/tmp/example-project'
PLAN_FILE='/private/tmp/example-plan.json'
mkdir -p "$TARGET_ROOT"
python3 "$FRAMEWORK_ROOT/scripts/v4_project.py" plan-init --root "$TARGET_ROOT" \
  --owner example-owner --project-id example-project > "$PLAN_FILE"
# Review the plan and copy its exact plan_sha256 before applying it.
PLAN_SHA='paste-the-reviewed-plan-sha256'
python3 "$FRAMEWORK_ROOT/scripts/v4_project.py" apply --root "$TARGET_ROOT" \
  --plan "$PLAN_FILE" --plan-sha256 "$PLAN_SHA"
python3 "$FRAMEWORK_ROOT/scripts/v4_local.py" inspect --root "$TARGET_ROOT"
```

Use `plan-import` instead of `plan-init` for an existing project. All plan commands
emit read-only JSON. Save the plan **outside** the target;
`apply --plan ... --plan-sha256 ...` checks
the exact plan and current target. `--root` must already exist. Git is never
initialized implicitly. Existing code, native agent rules, dirty and untracked
files are preserved. A conflicting BOOTSTRAP file is reported, not overwritten.

The installer creates immutable versioned guides and a stable BOOTSTRAP pointer.
Upgrades add assets; they do not rewrite task state, retarget existing contracts or
invent authorization. Both installers share WP-001's file planning and v2 rollback
ownership checks; its new `dry_run` option performs the same rollback preflight
before recording a project rollback intent. Old receipts cannot delete newer claims.

For an upgrade, set `FRAMEWORK_ROOT` to the newer reviewed checkout, keep
`TARGET_ROOT` unchanged, then run `plan-upgrade`, review and apply that new plan.
The CLI uses its checkout's version and guide; running the same version again
does not demonstrate a cross-version upgrade. Guide content changes require a
new version directory. To undo an upgrade, copy its returned `transaction_id`
and run the newer reviewed controller:

```sh
TRANSACTION_ID='paste-the-upgrade-transaction-id'
python3 "$FRAMEWORK_ROOT/scripts/v4_project.py" rollback --root "$TARGET_ROOT" \
  --operation-id "$TRANSACTION_ID"
python3 "$FRAMEWORK_ROOT/scripts/v4_local.py" inspect --root "$TARGET_ROOT"
```

See [the complete CLI example](../../examples/bootstrap/README.md) for plan and
receipt paths. Rolling back an upgrade restores the previous selection; rolling
back the initial installation removes its unchanged owned assets, including the
initial authority, and is not the same operation.

Installation intent and per-file receipts precede success. A final committed
receipt can reconcile a lost journal update. Unrecorded writes stay unknown and
block new installation/task writes; no guessed deletion. Rollback only deletes
unchanged owned assets and refuses live/unknown execution, changed initial state
or references to assets being removed. Git and user assets are never deleted.
The lock inode and transaction history are retained after rollback.

The first installation journal embeds the zero-write receipt intent. If the
process dies before the separate receipt exists, `rollback --operation-id ...`
can validate that intent and abort the installation, then a fresh `plan-import`
can proceed. Any existing planned output is still an unknown write and blocks this
recovery, even if its bytes happen to match. Old journals without that intent are
preserved for inspection; recovery does not invent missing ownership evidence.

## Verification

Regression groups: `tests/install`, `tests/protocol`. New groups: `tests/local`,
`tests/bootstrap`. Run each using a fresh unittest loader. All candidate tests must
run in an independently enforced no-credential/no-network sandbox with writes
limited to disposable fixture directories. `V4_OUTER_SEATBELT=1` describes that
actual environment; it does not enable sandbox protection by itself.

High-risk acceptance needs an independent non-author rerun against the exact
commit. The project's separate Issue #3 operations broker now has actual receipts
from delivery to an existing Codex session. Those operational transport receipts
do not implement or validate a product provider adapter, the external launcher,
or the full V4 scheduling and recovery workflow.
