# Independent probe-result admission verification

The non-author reviewer inspected the two-line production change before execution. `observe()` now rejects a `probe-result` unless `available` has exact Python type `bool`, before updating `last_observation`, the quota group, or any other in-memory state. Missing values, null, strings, numbers (including 0/1), lists and objects cannot masquerade as a completed negative observation.

A new protected source copy and independent T/C fixture were used. Six actual A01 canaries passed before the candidate unit suite: trusted write, outside read, checkout write, trusted-file hardlink alias, localhost networking, and credential-environment checks. Candidate modules were imported only inside the sandbox. No model, provider command, network probe, session creation, permission change or production broker deployment occurred.

The full `test_lifecycle.py` suite passed **24 tests in 72.299 seconds**, zero skipped, exit zero, with all 28 copied inputs unchanged. This reuses the author's test design but constitutes a separate execution in a new fixture. The three new tests check:

- Missing availability leaves in-memory state, persistent authority, operation receipts and outstanding probe unchanged.
- Ten non-boolean inputs are rejected without mutation; neither integers nor floats alias booleans.
- Explicit `False` settles only the matching completed probe and preserves the limit/backoff. A subsequent matching `True` permits recovery.

Existing quota-generation and duplicate-operation regression cases also ran. This is controller input validation, **not** independent proof that a real provider probe completed. A future trusted observer must still establish actual completion before emitting either boolean value; unknown outcomes must stay pending.

Evidence: `result.json` contains exact argv/environment, exit, timing and before/after hashes; `stderr.log` contains the unittest results; `canary-result.json`, `canary.stdout.log` and `profile.sb` record isolation. `REVIEW-INPUTS.json` maps repository-relative paths to the 28 tested byte hashes for commit binding by the Project Lead. The key reviewed hashes are:

- `framework/local/lifecycle.py`: `54945644488e9e86bd3918842362c6b692491705d84a7e9bbac9f87633ab3db5`
- `tests/lifecycle/test_lifecycle.py`: `f86252a7b65812bed52bf9d73dfb1995aa771d994ab7958555eaf602fda430f9`

`FILE-MANIFEST.json` separates raw and public-copy fingerprints. Machine paths are replaced only in public copies; original execution records and protected source copies remain outside the repository. Existing historical evidence was not rewritten, and unrelated handoff/demo suites were not repeated for this two-line change.
