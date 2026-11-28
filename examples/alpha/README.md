# Run the local Worker lifecycle preview

This first runnable increment is a **synthetic failure-injection demonstration**,
not a real Claude Code/Codex session or complete Lite Alpha. It uses actual Git
worktrees, files, processes and atomic task state, with a deterministic third
Adapter fixture. It makes no model calls and needs no model credential.

On the tested macOS environment, use the independently reviewed exact version of
`scripts/run_worker_demo.py`. Python `-I -S` is required. The helper imports only
stdlib on the host and freezes source/dependencies before sandboxed execution.
It does not install dependencies or alter the current repository. Supply an
existing **system-Python-compatible** directory containing jsonschema and its
dependencies (including native rpds for this interpreter/architecture).

From this reviewed checkout:

```sh
/usr/bin/python3 -I -S scripts/run_worker_demo.py \
  --source "$PWD" \
  --dependencies /absolute/path/to/existing/site-packages
```

The helper prints a new evidence directory under `/private/tmp/v4-worker-demo-*`.
Inspect `T/result.json`, `T/stdout.log`, `T/stderr.log`, `T/inputs.json`, and
`C/project/demo-evidence/summary.json`. A new run always gets a new isolated
project; it never reuses or deletes a previous project. Do not run an unreviewed
checkout's launch helper on the host. Do not fake the sandbox environment flag
to run `v4_worker_demo.py` directly.

The eight isolation probes must pass before the demo runs. Source and trusted
records remain unwritable to the candidate; candidate code cannot read external
files, use credentials or connect to the network. The exact process-information
restriction is part of the reviewed policy. Failure preserves the experiment.
Timeout reports unknown descendant termination rather than killing PIDs read
from candidate output or automatically replaying unknown work.

The demonstrated chain is:

1. Register three fixture Workers, each with capability, identity and quota-group
   bindings; use the third Adapter through the registry without vendor branches
   in the scheduler or recovery protocol.
2. Atomically assign two nonconflicting tasks and run two actual fixed processes
   simultaneously in separate worktrees.
3. Inject an explicit quota event; fence A and reject reassignment while its
   process outcome is unknown. B can continue its unrelated task.
4. Terminate/wait A through its owned process handle; preserve dirty tracked and
   untracked files in a pinned checkpoint and confirm the process group is gone.
5. B completes its own delivery, obtains a higher token for A's task, and restores
   the checkpoint into a new worktree. The old directory is preserved.
6. Inject the matching recovery probe result. A returns to the pool without
   taking back B's assignment. Reject old-token and duplicate submissions.

The probe uses controlled observation time; it is not evidence of a real vendor
reset or wall-clock recovery delay. `pmo_model_calls=0` proves the deterministic
fixture does not need an online PMO model. Delivery capture still reports
`engineering_accepted=false`; the demo does not invent a review, merge or business
acceptance. The third fixture's process launch is the explicitly fixed demo
supervisor, not a general native `Adapter.start` implementation.

## Verify the first delivered artifact

After independent review of the exact updated launch-helper bytes, opt in to a
real fixed-Python evidence run for the first completed delivery:

```sh
/usr/bin/python3 -I -S scripts/run_worker_demo.py \
  --source "$PWD" \
  --dependencies /absolute/path/to/existing/site-packages \
  --verify-first-delivery
```

The first completed delivery is WP-B's `src/b/output.txt`. The helper compares
the actual worktree file with the captured delivery bytes and hash, then freezes
those bytes with a fixed Python checker and a provenance record. A new temporary
Git repository produces a **verification capsule commit** for that exact file
set. Its SHA is separate from the development baseline; it is not a claim that
the Worker committed new code. The original project and its task state remain
unchanged by collection and verification.

The independently reviewed, hash-pinned collector runs the checker in its own
Seatbelt sandbox. The expected bytes are fixed by the example specification,
independently of the captured output. The public quality CLI then verifies the
protected receipt, logs, policy, source, plan and trust pin in a separate sandbox.
No framework module is imported on the host. The collector is launched outside
the original candidate sandbox, so this path does not depend on nested Seatbelt.

Inspect `T/quality/result.json`, `T/quality/plan.json`, `T/quality/trust.json`,
`T/quality/capsule.commit`, `T/quality/evidence.json`, `T/quality/logs/`,
`T/quality/gate.stdout.log` and the recorded process launch/results. The main
`T/result.json` includes the quality result. The actual checker's stderr and the
Gate stderr record their isolation probes. A successful collection process can
still contain a failed check: only the separate Gate result decides whether
this artifact check passed.

This mode checks a **document artifact**. The demo's Work Package still has its
original code-task metadata; a text check does not satisfy code engineering
acceptance. `engineering_accepted=false` and `provider_live=false` remain true
limitations even when the artifact Gate passes. The Gate binds the frozen
snapshot, not continuing immutability of the original live workspace. The
helper checks source/authority stability around collection and preserves any
failure, but makes no hostile same-OS-user authentication claim.

An unknown demo process outcome prevents collection. An unknown collection
prevents Gate execution and automatic retry; the exclusive collector intent and
all partial evidence are retained. Never reuse that evidence directory to rerun
unknown work. The flag adds no provider call, paid service or background task.

Existing-project onboarding, general task authoring, native provider launch/
monitor/cancel, unattended live probes, operating-system service installation,
real quota recovery and a second machine remain separate implementation or
verification items. Dedicated/elastic/restricted mode names are metadata in this
increment, not fully enforced contribution policies. Prepared-but-never-launched
tasks are preserved and block automatic handoff until a trusted no-writer
reconciliation path exists; the positive demo covers a running owned process.

Use `scripts/v4_worker.py inspect --root <the-generated-project>` **inside the
same reviewed execution boundary** to inspect state. Its `cycle` operation can
produce reservations and durable probe intents without a model; it currently
does not execute provider calls. The project task authority stays in one state
file, not a second queue maintained by this example.
