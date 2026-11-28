# Local worker lifecycle increment

This is a deterministic controller, not an AI PMO. Worker runtime, quota groups,
task assignments, fencing, operation receipts and artifacts share the existing
`.ai-org/state.json` atomic authority. A local process lock and expected revision
serialize writers. No GitHub or remote authority backend is deployed here.

`scripts/v4_worker.py` exposes inspected state, explicit lifecycle enablement,
trusted observations, bounded scheduler ticks and capability-based dispatch.
`cycle` performs ticks and matching without any model call. It returns persistent
probe intents and task reservations; it does not yet execute provider probes or
models. A lost probe response remains pending for reconciliation, never a blind
second model request. The reviewed observer must resolve it from actual evidence.
No scheduler service is installed by importing or running `inspect`.

Worker runtime separates its eight lifecycle states from work-package state and
legacy Worker presentation. Agent tool, model provider, actual model and credential
reference are optional opaque metadata; unknown values stay null. Auth identity,
quota group, Host, Worker, role and per-assignment Session remain distinct. The
controller has no vendor-name branches. Registry membership and role grants are
trusted operator actions, not claims supplied by a joining remote machine.

Quota groups affect all member Workers. A restriction fences existing assignments
and pauses affected tasks; it does not mark engineering failure or discard output.
Other independent groups can continue. A healthy heartbeat cannot clear quota,
authentication, budget, Owner pause or uncertain stop. Retry-at is nullable;
locally computed next-probe-at is explicitly policy, not a vendor reset promise.
Repeated limits preserve the current attempt budget. Probe results bind a durable
generation/attempt ID. Only a trusted project-budget event changes project budget;
per-call or session limits cannot stop unrelated resources.

The single-host controller still trusts its operator and cooperating processes
under one OS owner. Actor IDs and booleans from that trusted observer are not
remote authentication or proof against a hostile host owner. Provider text cannot
be passed directly as a trusted observation. Enabling lifecycle never upgrades
unknown quota or absent credentials to available.

`framework.local.handoff` connects real filesystem snapshots to authoritative
assignment and checkpoint pins. It rechecks baseline, specs, scope and unknown
operations before a new claim. Stop confirmation requires the controller's owned
process handle, matching registered PID/group, completed wait and absent process
group; the launcher must prevent process escape. A PID copied from a file is not
enough. This does not establish an arbitrary native CLI process-tree guarantee.

Handoff restores into a new registered worktree while preserving the previous
directory. A durable restore intent prevents partially restored output being run
or delivered. Unknown external operations block; a model's claimed reconciliation
cannot clear them. Session-native recovery is optional; file checkpoint recovery
does not depend on restoring another vendor's native Session.

Dedicated, elastic and restricted are registered contribution modes. This
increment records them; time-window scheduling, restrictions beyond existing
role/scope/capability checks, remote invites and cross-host authentication remain
unimplemented. Do not describe these metadata values as enforced enrollment
policies. Provider preferences, quality history and costs require reliable inputs;
the current matcher uses eligibility, capability, scope and capacity then stable
IDs, and does not invent quality/cost scores.

The next product gate remains two real CLI Workers plus the injected failure
journey. Metadata/help checks, synthetic processes and genuine quota recovery
have separate evidence levels. This component alone is not Lite Alpha acceptance.
