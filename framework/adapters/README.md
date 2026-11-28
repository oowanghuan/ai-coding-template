# Adapter invocation wiring

The registry supports N tool/provider selections. Default adapters still provide
nonexecuting proposals and result parsing. An application must explicitly bind a
reviewed executor before declaring start/status/stop supported. No model, login,
network or process is started by registration or planning.

`ProcessExecutor` is a local process transport for a trusted supervisor. Its
constructor fixes argv, cwd, explicit environment, content-pinned executable and
configuration files, a protected journal root, a live authorization checker, and
a mandatory `LaunchReservations(shared_root)` bound by the trusted controller.
Agent output cannot choose those values. It does not turn the proposal's
`execution_authorized=false` into permission: the controller must check current
Assignment, epoch/token, lease, Worker/Host, scope and budget before launch.

Register the executor using `registry.register(descriptor, planner=...,
classifier=..., executor=...)`. The descriptor and executor must have exactly the
same selection. Operations are:

- `registry.start(adapter_id, operation_id=..., authority=..., **request)`:
  authority has assignment_id, workspace_id, epoch and token; request uses the
  existing bounded work-package, assignment, baseline, prompt and limit fields.
- `registry.status(adapter_id, invocation_id)`: observed process state, not a
  work-package milestone. A restored controller without the owned handle reports
  outcome_unknown for an unfinished record.
- `registry.stop(adapter_id, invocation_id)`: request termination of the owned
process. Poll for its actual exit; do not interpret this return as stopped.
- `registry.result(adapter_id, invocation_id)`: bounded captured stdout/stderr,
  hashes, exit code, exact binding and input identity. Changed output is rejected.
  With StoreBinding, this also idempotently records a terminal process observation
  in the Store. A failed/lost Store write can be reconciled by reading the result
  again; it never restarts the process. Early stop may leave output uncaptured;
  these hashes bind captured bytes, not a claim of complete provider output.

The **shared launch reservation root** spans all adapters and controller
instances of the resource pool, including replacement controllers. It must be
persistent, protected from candidates, and fixed by application configuration;
never allocate one per adapter, retry, or session. The registry rejects mixed
launch domains. Separate registries/controllers must use that same root too;
independently configured roots cannot fence each other. Real deployment must
verify this wiring against the project's authoritative Store before admission.

Under a common OS file lock, the reservation records Assignment, workspace ID,
canonical working directory, invocation/binding and selection **before** the
per-binding journal and spawn. Any existing Assignment/workspace reservation or
equal/nested working directory rejects a new launch, irrespective of adapter,
operation ID or token. Reservations never expire or release automatically here.
A crash between reservation and local journal leaves an uncertain reservation
that blocks retry; local receipt loss cannot grant another spawn. Another
workspace with independent authorization can proceed. The reservation journal
is a launch fence, not a second task authority and not authorization by itself.

The per-binding journal records execution observations and bounded output.
Same operation and intent returns the previous invocation; different intent is
rejected. Invocation IDs include the fixed binding, so independent bindings may
share an output directory and operation name without reading one another's
status as their own. A crash/unknown launch is never silently retried. A
different operation ID cannot repeat an already-bound authority/workspace,
even after exit; higher fencing tokens do not authorize reuse of that workspace.
The direct-local-only recovery namespace is
rejected in cwd, journal paths and fixed argv, including case variants.
Thread supervision drains both pipes with a combined size cap and a deadline;
no parent environment is inherited implicitly.
Post-spawn initialization is also guarded: failure to create/start supervision,
create a selector, set pipe mode or register pipe events attempts stop/wait on
the owned handle and retains outcome_unknown. Partial resources are closed
individually so one failed close cannot skip the rest. If stop/wait or journal
writing fails, the original launch intent remains unresolved; no retry/release
is authorized. Initialization faults do not fabricate complete output evidence.
Output is untrusted_stdout and engineering_accepted=false. All records retain
writer_stop_confirmed=false: observed exit of one owned process does not prove
that every descendant or outside writer has stopped. Existing handoff proofs
remain necessary before reallocating write authority.

This module is not a sandbox or deployed service. Use a pinned, independently
reviewed supervisor and the existing approved CLI execution boundary. Candidate
work must not modify the journal, executable or configuration. System executable
hardlinks are allowed with exact content pins; symlinks are rejected. Journal and
output files retain single-link checks. Pin checks cannot substitute for immutable
deployment when an attacker can concurrently replace an executable.

This revision changes binding/ID derivation. It is for fresh, never-launched
workspaces; it does **not** migrate or rearm historical invocation records.
Before any upgrade with existing work, reconcile/import all outstanding intents
into the common fence under the existing authority, or keep those workspaces
blocked. Do not create an empty reservation root to bypass historical uncertainty.
No migration or production deployment is performed by this component.

`tests/adapters/test_invocation.py` runs real fixed Python processes through this
interface. It does not start Claude, Codex, or another model. The fixed factory
below assembles reviewed application inputs; actual credential/health probes,
complete Store recovery, continuous supervisor restart and real provider execution remain separate
integration work. The lifecycle journal contains execution observations and
cannot grant or replace the project's authoritative Assignment.

## Local Store binding

`StoreBinding` in `store_binding.py` connects the existing local authority to
this transport. Construct it with the project root, shared protected reservation
root, actor, exact Assignment/epoch/token/workspace, selection, and fixed cwd.
Use the **same object** for `ProcessExecutor(launch_reservations=bridge,
authorize=bridge.authorize, ...)`. Registration or construction does not launch
anything. The default registry still has no automatically enabled real executor.

At each authorization check it reads the Store under its existing lock and
checks active ownership/lease, project budget/pause, current authorization and
contract fingerprints, dependency consistency, current Worker health/auth/host
and shared quota status, registered resource selection, restored checkpoint,
registered Git worktree and actual baseline. The bridge exposes a frozen `scope`
for trusted factory wiring; checking it does not itself restrict filesystem
writes. The reviewed execution boundary must enforce those paths before any
real CLI is admitted.

Before spawn, the bridge atomically records `provider-run-begin` and the
workspace's `launching` intent in the **same Store**, marks writer stop unproven,
then reserves the shared launch fence. Failure after either write remains
unresolved; it never rolls back an uncertain launch or issues a replacement
permission. A second authorization check observes changes before spawn. The
original bound object can recognize its own committed intent; a replacement
controller cannot treat a persisted intent as a new start permission.

Transport exit/result stays an observation. Reading a protected terminal result
records the matching invocation and output fingerprints in Store, setting the
workspace to `unknown` pending writer reconciliation. Replay adds no revision or
new operation; changed observations are rejected. This does not auto-submit,
accept, release or mark a workspace finished based only on a parent exit code.

### Runtime authorization and stop

ProcessExecutor automatically binds StoreBinding's `runtime_authorize` and
`observe_terminal` hooks together. Without those hooks, the plain process
transport reports runtime authority support as false; it does not claim live
authorization monitoring. No callback or policy can be supplied by Agent output.

A separate read-only monitor checks the Store immediately after spawn, then
waits 0.25 seconds between completed checks. The process supervisor remains
independent of that check: denial, exception, or no successful observation for
2 seconds triggers a kill/wait of its **owned main process**. A late successful
check cannot reset an already expired observation. Supervision begins before
the post-spawn journal write, so a slow write cannot defer the stop loop. The
record distinguishes authority_revoked, authority_check_error and
authority_check_timeout. Stale/failing checks do not cause repeated launches.

This is bounded polling under a functioning OS scheduler, not instantaneous
kernel permission revocation. The last-check-to-spawn window can still start a
process; the tested behavior is subsequent owned stop, not zero executed
instructions. The fixed-process tests declare a 5-second observed stop bound;
that is not a real-provider SLA or a guarantee during OS suspension/starvation.
A stuck read-only callback can outlive the process and delay Store writes, but
does not block the separate stop loop. Terminal observation can be retried after
Store availability returns without restarting work.

Only the owned main process is killed. Descendant/outside writer termination,
final checkpoint validation, safe handoff and real-provider side effects remain
separate deployment gates. `writer_stop_confirmed=false` remains unchanged; no
automatic recovery/release is granted by this monitor. The fixed CLI factory
below is not an installed continuous host service or a live admission proof.
`tests/adapters/test_store_binding.py` covers real local Store/Git plus fixed
Python processes under A01, with synthetic authentication/quota observations.

## Fixed application factory

`factory.bind_store_adapter(registry, descriptor, ...)` binds one prepared
workspace and resource selection to the Store bridge and fixed process transport.
The reviewed application supplies planner/classifier callables, fixed argv and
environment, pinned binary/config files, protected shared reservation and journal
roots, actor/authority/cwd, and a mandatory trusted `boundary_check` callable.
Nothing is discovered from project configuration, PATH, model output or entry
points. Construction and registration never start a process or write task state.

The boundary checker receives a detached manifest containing execution binding
hash, Store/authority/contract/scope, selection, argv, fixed roots and file pins.
Environment values are hashed, not returned in that manifest. Do not put secrets
in argv or config metadata; credential references are opaque identities only.
This is not a credential manager or proof that a supplied callback is trustworthy.

The checker must verify the actual immutable deployment and effective isolation,
tool/configuration closure, credential/network and spending boundaries. A boolean
from candidate JSON is not such a check. Missing, unknown, false or throwing
checks fail closed; the same checker runs at launch and under the runtime watch.
An accepted boundary does not override Store permission, quota, budget or lease.
No always-allow production checker is provided. Applications must not deploy
this candidate factory merely because synthetic tests pass.

`bind_native_store_adapter(..., tool=..., binary=..., ...)` provides the first two
concrete recipes (`codex`, `claude-code`), reusing `runspec.py` without extra flags
or session-resume input. It verifies the declared Agent Tool and derives the
model flag from the same descriptor used by the Store. It does not infer the
Model Provider from the tool. A third reviewed tool uses `bind_store_adapter`
without changing the Scheduler, state machine or Recovery Protocol.

Capabilities are promoted only for the implemented invocation operations;
validation level, native resume, authentication and recovery are not promoted.
The default registry remains nonexecuting. The first two native recipes have
assembly-only tests; the common factory is exercised with real fixed Python
processes and synthetic state, separately from still-pending real CLI admission.
