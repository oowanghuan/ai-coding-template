# Independent timing-defect verification

This package responds to Advisor comment [7236044988](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7236044988). The reviewer did not implement either production fix. It includes an independently authored reproduction and reverse verification, followed by reuse of the frozen lifecycle/handoff and synthetic demo regression tests. Candidate code ran only under the existing A01 policy in a fresh private T/C fixture; no model, provider probe process, remote API, permission change, or service installation was used.

## Both defects reproduced on the actual old code

The reviewer copied 30 source/schema/test files from Git commit `1552a59b2e908535f9ed6938217b1fd0c8c6cf39` into a protected baseline tree. Six boundary canaries passed before execution. The reproduction exited zero because both specified incorrect outcomes were observed; that exit is **not** a product acceptance result.

- Quota: emit generation-1 probe, then commit a new group limit with a later retry time, then deliver the old success. The old version cleared both the limit and retry time.
- Snapshot: create a checkpoint, let a real owned child receive a pipe instruction and write final bytes, observe its exit zero, then confirm stopping and hand off. The old version accepted the earlier checkpoint and restored the earlier bytes instead of the child's final bytes.

The old source manifest, exact reproduction script, actual command/environment, exit code, before/after hashes and output are in `baseline-manifest.json`, `reproduce.py`, `baseline-result.json`, and `baseline.stdout.log`. Baseline inputs remained unchanged.

## Independent reverse verification on the fix

The fixed tree contains 32 exact inputs. Every input was independently compared against the Git blob at `03e7eaaf14b62a3b48b970df0ed877d3b3aab33f`; all matched (`commit-binding.json`, `REVIEW-INPUTS.json`). Runs use this protected copy so concurrent checkout documentation edits cannot change the tested version.

The independently authored `verify_fixed.py` exited zero with unchanged inputs and verified these concrete sequences:

1. A new limit increments the observation generation but retains the old outstanding probe. Even when the retry time arrives, no second probe is emitted while the first result is unknown. The late old success resolves only that old intent; the group stays limited, preserves retry/backoff and attempt count, and reports the result stale. Only a newly issued current-generation probe can restore availability.
2. The actual writer changes the workspace after its checkpoint and exits. Stop confirmation rejects the stale snapshot, authority bytes remain unchanged, and a new claim remains blocked. The old directory keeps the final bytes. After a new post-stop checkpoint, confirmation and handoff succeed and the new workspace contains those final bytes.

See `fixed-adversarial-result.json` and `fixed-adversarial.stdout.log`. The frozen lifecycle/handoff suite passed all 36 tests in 258.673 seconds; the fixed demo suite passed all three tests in 54.467 seconds, including completed-delivery recovery replay. Both exited zero with no skipped tests and all frozen inputs unchanged. Exact commands, environments, stderr summaries and hashes are in `fixed-lifecycle-result.json`, `fixed-lifecycle.stderr.log`, `fixed-demo-result.json`, and `fixed-demo.stderr.log`. The completed-recovery fixture retained its real synthetic process journal, final authority and replay result under `demo-completed-recovery/`. No earlier test evidence was replaced.

## Scope and remaining limitations

This closes the two specified local state-ordering defects; it does not establish real provider quota recovery or cross-service exactly-once effects. Probe observations here are injected trusted-controller inputs with an explicit boolean availability result after a completed observation. Missing, malformed, and unknown provider responses are not exercised here. In particular, the existing controller treats an absent availability value as false; real integration must validate completed observations before emitting this event. The implementation intentionally keeps an unanswered old probe pending rather than falsely declaring its external operation cancelled.

Workspace checking covers regular-file content, size, executable bit, directory listings (including empty-directory changes), and HEAD against the latest snapshot; it checks before stop admission, claim, and around restore. It assumes the owned writer has actually stopped and no other authorized writer continues modifying that directory. This is not an atomic filesystem snapshot or protection against an adversarial machine owner.

The existing restore path does **not** promise complete empty-directory topology equivalence in the destination: it restores files, and empty-directory reconstruction/removal is outside this repair. Directory changes in the old workspace are detected; that must not be confused with complete directory restoration. Git administrative metadata is excluded from the content snapshot, while HEAD is separately checked. Real Claude/Codex execution and engineering-gate integration remain unverified.

## Provenance

`FILE-MANIFEST.json` keeps original and public-copy SHA256 separately. Machine paths are replaced in public copies; originals remain outside the repository. Result values and counts are not rewritten. The copied code snapshots remain outside the repository and can be reconstructed from the bound commits and manifests. `REVIEW-INPUTS.json` contains only repository-relative paths and exact tested hashes. The independent harnesses, their outside-repository execution records, and the reused product tests have distinct provenance; this report is not itself an engineering Evidence Gate receipt.
