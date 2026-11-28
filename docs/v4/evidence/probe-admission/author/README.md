# Probe-result admission — author evidence

This package records author reproduction and verification of strict boolean admission for `probe-result.available`. It is not an independent review. Candidate code ran only under the previously reviewed A01 sandbox, with no credentials or network. The tests used real temporary Git/authority files and synthetic quota observations; no real provider probe, provider model call, or external API executed.

| Run | Scope | Tests | Passed | Failed | Errors | Skipped | Exit |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Before correction | Three new admission tests | 3 | 1 | 2 | 0 | 0 | 1 |
| After correction | Complete `test_lifecycle.py` suite | 24 | 24 | 0 | 0 | 0 | 0 |

Both runs passed five isolation canaries: external file read denied, external file write denied, checkout write denied, network connection denied, and credential environment absent. Each run's five tracked source/schema inputs remained unchanged. This fingerprints those five files, not every transitive dependency. Exact argv, UTC timestamps, hashes, stdout/stderr and source snapshots are retained in the corresponding `before-*` and `after-*` files/directories.

## Change and assertions

Previously a missing field or `null` reached the negative-result branch and cleared a pending probe. The two pre-correction failures preserve that behavior; the nonboolean loop stopped at its first invalid value, so the pre-run does not claim to have executed every malformed variant.

The correction checks `type(payload.get('available')) is bool` before the first mutation in `observe`, including before `last_observation` is updated. Missing values and ten nonboolean variants (`null`, three strings including empty, integers 0 and 1, floats 0.0 and 1.0, array and object) are rejected. After correction, the tests verify unchanged in-memory state for direct observation and unchanged authority bytes/operation receipts through the public Store entry. The unresolved probe stays pending.

The positive test executes explicit `False`, confirms a recorded negative observation, preserved limit and scheduled backoff, then executes a fresh matching probe with explicit `True` and confirms the limit clears. Existing generation, stale-response, quota-group, attempt-budget, heartbeat and idempotency tests also pass. This is protocol admission validation, not proof of provider authentication or real provider quota availability.

Frozen corrected source fingerprints:

- `framework/local/lifecycle.py`: `54945644488e9e86bd3918842362c6b692491705d84a7e9bbac9f87633ab3db5`
- `tests/lifecycle/test_lifecycle.py`: `f86252a7b65812bed52bf9d73dfb1995aa771d994ab7958555eaf602fda430f9`

## Public copies

`manifest.json` distinguishes original raw-byte hashes from redacted public-copy hashes. Original artifacts remain outside the repository. Personal source/dependency/fixture paths have been replaced with `/public/source`, `/public/dependencies`, `/public/fixture`. These review copies are not byte-identical substitutes for path-bound original execution artifacts; placeholder paths are not directly runnable. No private-project material, native session identifiers, credentials or provider response data is included.
