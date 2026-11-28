# Adapter invocation wiring

The registry supports N tool/provider selections. Default adapters still provide
nonexecuting proposals and result parsing. An application must explicitly bind a
reviewed executor before declaring start/status/stop supported. No model, login,
network or process is started by registration or planning.

`ProcessExecutor` is a local process transport for a trusted supervisor. Its
constructor fixes argv, cwd, explicit environment, content-pinned executable and
configuration files, a protected journal root, and a live authorization checker.
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
- `registry.result(adapter_id, invocation_id)`: bounded stdout/stderr, hashes,
  exit code, exact binding and input identity. Changed output is rejected.

The protected journal records intent before spawn. Same operation and intent
returns the previous invocation; different intent is rejected. A crash/unknown
launch is never silently retried. Thread supervision drains both pipes with a
combined size cap and a deadline; no parent environment is inherited implicitly.
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

`tests/adapters/test_invocation.py` runs real fixed Python processes through this
interface. It does not start Claude, Codex, or another model. The factory wiring
for real providers, Store authorization integration, credential/health probes,
continuous supervisor restart and real provider execution remain separate
integration work. The lifecycle journal contains execution observations and
cannot grant or replace the project's authoritative Assignment.
