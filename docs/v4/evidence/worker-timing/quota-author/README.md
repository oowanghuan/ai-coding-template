# Quota generation race — author reproduction and fix

This is author verification of the quota-generation correction, using the existing lifecycle suite plus author-added regressions. It is not independent approval. All candidate code ran under the previously reviewed A01 Seatbelt harness, with no credentials or network. The suite creates real temporary Git/state files; quota observations and probe responses are synthetic protocol fixtures. No provider or physical quota-probe process was launched.

## Recorded outcomes

| Execution | Tests | Passed | Failed | Errors | Skipped | Process exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Before correction | 20 | 17 | 3 | 0 | 0 | 1 |
| After correction | 21 | 21 | 0 | 0 | 0 | 0 |

Both runs passed five isolation canaries (outside read/write denied, checkout write denied, network denied, credential environment absent). Each run's five tracked source/schema inputs were unchanged during that run; this is not a claim to fingerprint all transitive dependencies. Raw stdout/stderr, exact argv and source hashes are in `before-*` and `after-*`. Matching source snapshots are retained under `before-source/` and `after-source/`. The after suite adds one additional failed-old-response/budget case, so the total increases by one.

## Reproduced defect and behavior after correction

An issued probe belonged to an earlier quota observation. A second worker in the same quota group then reported a newer limit and extended `retry_at`. Previously, the earlier successful probe response cleared that newer limit; the pre-correction regression logs preserve the actual failures.

Each distinct committed limit observation now advances the group's generation. Operation replay remains idempotent. An outstanding old probe is retained, and scheduler ticks cannot issue a replacement while its outcome is unknown. A response matching that outstanding intent can settle the old operation; the receipt explicitly marks `stale_probe_result: true`. Neither old success nor old failure clears the newer limit, changes its retry/backoff, or resets its attempt budget. A fresh-generation success can clear the limit only after the prior intent is settled and the new retry window permits another bounded attempt.

The tests cover the shared group of two workers, unaffected third worker, old success and failure, pending intents across ticks, the retry window, exhausted attempt budget, same-operation replay, and rejection of a new operation ID attempting to consume an already settled probe. Generation follows committed authority order; it does not rely on an observation timestamp to restore availability. Unknown physical outcomes are not declared cancelled or stopped.

Frozen corrected inputs:

- `framework/local/lifecycle.py`: `6eec3315d202f890c220fc0357967e8d18eacb38e40183f06fa6767f100ed057`
- `tests/lifecycle/test_lifecycle.py`: `fd243e046f753f5f210713ac0bf8ae62f59c35ec41263c0e1cbcbfafc6ecf647`

## Public-copy provenance

`manifest.json` separates original raw-byte SHA256 values from public-copy SHA256 values. Personal source, dependency and experiment paths are replaced with `/public/source`, `/public/dependencies` and `/public/fixture`. Original files remain outside the repository. The copies are review evidence, not byte-identical substitutes for original path-bound execution artifacts; placeholder paths are not runnable as-is. This publication includes no credentials, native sessions, private-project content, or remote-service execution evidence.
