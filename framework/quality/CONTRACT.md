# Local quality interface 1 (WP-201 / WP-203)

This batch assumes a reviewed operator provisions a protected trust file, plan,
collector and source snapshot. Candidate code cannot write these or the receipt
directory. A directory name or caller-supplied hash is not proof of this boundary.
The calling operator pins the trust-file hash out of band. No hostile host-owner,
remote identity or test-completeness guarantee is claimed.

## Collector input

`collector.py --plan /T/plan.json --plan-sha256 <raw-byte-sha256>` is a standalone
stdlib finite program. Execute a host copy only after independent review/pinning.
Never import candidate modules in the host collector. Candidate code runs only in
the collector's fixed macOS Seatbelt/Python adapter. Environment variables are
allowlisted, network access and other-process information reads are denied.

Plan exact fields:

```
format: quality-plan/1
run_id, wp_id: nonempty bounded identifiers
wp_revision: positive integer
kind: code | document
trusted_root: canonical absolute T (plan, collector, subject, output logs/receipt)
scratch_root: canonical absolute C, disjoint from T, writable only in per-case sandbox
subject_root: T/subject
entrypoint: relative Python file in subject_root
subject: {commit: git SHA1, tree: git SHA1, manifest_sha256: canonical manifest SHA256}
commit_object: raw Git commit object body as UTF-8 string
manifest: {relative_path: {sha256: file SHA256, mode: "100644" | "100755"}}
collector_sha256: approved collector file SHA256
environment: {platform: darwin, python: /usr/bin/python3, python_version,
              sandbox: macos-seatbelt}
tests: [{id, required: bool, input: string, expected_exit: integer,
         expected_stdout_sha256: SHA256, timeout_seconds: integer,
         skip_reason: null | nonempty string}]
```

Canonical JSON is UTF-8, sorted keys, separators comma/colon, ensure_ascii=False,
allow_nan=False. Duplicate JSON keys, nonfinite numbers, links, path traversal and
unexpected fields fail closed. Test IDs are unique. At most 32 cases, input at most
64 KiB/case, timeout 1..30 seconds, aggregate declared timeout at most 120 seconds.
expected_exit is a non-bool integer 0..255. Both code and document require at least
one executed check to pass. Environment is pinned in the plan and checked against
the actual system Python version/platform. This finite adapter does not support
candidate subprocess creation: the child sandbox denies process-fork.
It also denies `process-info* (target others)`: clearing the environment alone
does not prevent macOS process-argument APIs from reading another process's
environment. Tests for this boundary target only an owned process with synthetic
canary data, never a real credential-bearing process.
The complete regular-file source snapshot must match the manifest and Git tree;
the raw commit body must hash to the declared commit and name that exact tree.
This binds regular-file contents and Git executable modes; empty directories and
filesystem timestamps are not Git objects and are not part of the subject hash.

Collector stores `intent.json` exclusively before execution, never overwrites or
repeats an existing run. Terminal result is `evidence.json` in T. Logs are relative
`logs/<case-id>.stdout` / `.stderr`. Each case uses only fixed argv:
`/usr/bin/python3 -I -B -S <subject_root>/<entrypoint>`; its approved input travels
over stdin. Parent computes result from observed exit, timeout and stdout bytes,
not from a candidate-reported test summary. This is a finite black-box stdio test
adapter, not arbitrary shell or a general unit-test/plugin engine.

## Evidence exact fields

```
format: quality-evidence/1
evidence_id: same run_id
wp_id, wp_revision, kind, subject: copied validated plan bindings
plan_sha256: raw plan hash
collector_sha256: actual fixed program hash
adapter: python-stdio/1
state: complete | unknown
started_at, finished_at: UTC ISO strings
environment: {platform, python, python_version, sandbox: macos-seatbelt}
source_unchanged: bool
cases: [{id, required, status: passed|failed|skipped|not_run,
         exit_code: integer|null, signal: integer|null, timed_out: bool,
         output_limit_exceeded: bool, collection_error: string|null,
         command: string[], pid: integer|null, cwd: string,
         input_sha256, expected_exit, expected_stdout_sha256,
         stdout: {path, sha256, size}|null, stderr: {path, sha256, size}|null,
         policy_sha256: SHA256|null, skip_reason: string|null,
         started_at: UTC|null, finished_at: UTC|null}]
counts: {passed, failed, skipped, not_run}
```

Protected trust file:
`{format: quality-trust/1, runs: {run_id: {root: T,
plan_sha256, collector_sha256, wp_id, wp_revision, subject}}}`.
It is provisioned by the reviewed operator, never derived from an uploaded report.
Gate loads only the registered run's plan/evidence/logs, verifies all bindings and
recomputes counts/outcomes. It does not run code or change task authority.

## Gate / governance API

`framework.quality.gate.verify_bundle(trust_path, expected_trust_sha256, run_id)`
returns deterministic JSON with `format: quality-gate/1`, `status:
passed|failed|unverifiable`, sorted `reasons`, `gate_id`, `evidence_id`,
`evidence_sha256`, `plan_sha256`, `trust_sha256`, `wp_id`, `wp_revision`, `subject`.
Unavailable bindings may be null in an unverifiable result. `gate_id` fingerprints
the decision's bound inputs and result, not a credential. All logs must be checked
before passed. Code with no executed checks, required skip/not_run, timeout, wrong
observed result or incomplete expected set cannot pass. Optional approved skip is
distinct. Parse/source/identity/receipt corruption is unverifiable, never passed.

WP-203's CLI calls this verifier against the operator-pinned protected trust input;
it must not accept a caller's serialized `status: passed` as proof. Pure governance
tests may inject a synthetic gate result but must be labelled as such. Signoff
authenticity is established separately by protected, pinned reviewer-source
records. Neither component advances merged/deployed/business acceptance.

Initial failure baselines are recorded as failures. WP-203 can compare verified
old/new check definitions, entrypoint fingerprints and observed outcomes to
classify known versus new failures. This version does not waive a failed Gate:
a valid deviation or remediation plan alone never makes it passed.

Actual policy bytes live at `T/policies/<case-id>.sb` and must match the case hash.
Stdout/stderr are individually bounded to 1 MiB. Exceeding either bound is recorded
explicitly and cannot pass even if the retained prefix matches an expected hash.

An interrupted collection or unknown child result stops the batch. The exclusive
intent and any logs are preserved. After an abrupt collector crash, process exit
is not automatically proven; the operator must reconcile the unknown operation
before selecting a new run ID. Re-running the old ID cannot launch another test.
