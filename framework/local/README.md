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
macOS does not support nested Seatbelt initialization. Inside an outer Seatbelt
test harness the full runner integration tests are explicitly skipped and a
failure-closed test must pass. Standalone worker/policy checks and controller tests
are separate evidence, not a substitute for an independent full integration run.

Fencing protects the controller and captured delivery. It does not assert that an
expired process has ceased writing its old directory. Captured files are bounded,
hashed, stored as bytes in the authority and returned with `accepted: false`.
No test report, review milestone, merge or business acceptance is inferred.

## Project installation

`scripts/v4_project.py plan-init|plan-import|plan-upgrade` emits a read-only JSON
plan. Save it **outside** the target; `apply --plan ... --plan-sha256 ...` checks
the exact plan and current target. `--root` must already exist. Git is never
initialized implicitly. Existing code, native agent rules, dirty and untracked
files are preserved. A conflicting BOOTSTRAP file is reported, not overwritten.

The installer creates immutable versioned guides and a stable BOOTSTRAP pointer.
Upgrades add assets; they do not rewrite task state, retarget existing contracts or
invent authorization. Both installers share WP-001's file planning and v2 rollback
ownership checks; its new `dry_run` option performs the same rollback preflight
before recording a project rollback intent. Old receipts cannot delete newer claims.

Installation intent and per-file receipts precede success. A final committed
receipt can reconcile a lost journal update. Unrecorded writes stay unknown and
block new installation/task writes; no guessed deletion. Rollback only deletes
unchanged owned assets and refuses live/unknown execution, changed initial state
or references to assets being removed. Git and user assets are never deleted.
The lock inode and transaction history are retained after rollback.

## Verification

Regression groups: `tests/install`, `tests/protocol`. New groups: `tests/local`,
`tests/bootstrap`. Run each using a fresh unittest loader. All candidate tests must
run in an independently enforced no-credential/no-network sandbox with writes
limited to disposable fixture directories. `V4_OUTER_SEATBELT=1` describes that
actual environment; it does not enable sandbox protection by itself.

High-risk acceptance needs an independent non-author rerun against the exact
commit. This implementation does not deliver Issue events to an existing Codex
session. That missing broker consumer remains a separate, unverified integration.
