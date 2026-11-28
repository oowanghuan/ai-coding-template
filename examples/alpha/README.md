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
