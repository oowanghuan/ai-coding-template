# Independent external client/controller review

Static review: exact config/request binding, integer limits, immutable publish, bounded regular-file/log reads, monotonic receipt sequence, stable PID, observed exit and matching logs before terminal status. Run intent is committed before request; fresh authority guards and workspace transitions fence delivery. Missing/invalid/unknown stop evidence preserves unresolved execution; known prelaunch rejection is stopped without a process; failed replay remains nonzero and cannot launch again. No blocking issue found in this bounded cooperative-controller design.

Independent A01 execution: 21 tests, exit zero. Actual Store and CLI lifecycle behavior is exercised, but driver receipts are explicitly synthetic fixture data. No real host driver was launched by these tests. Six source files were hashed before/after with no changes; result.json records hashes, commands, environment and elapsed times.

Security limit: ExternalClient configuration path declarations alone do not prove that trusted storage is actually protected. The external coordinator must establish the OS boundary, pin config/program hashes and inspect original protected receipts/logs. This CLI is not a hostile-controller-resistant general evidence gate.

The staged coordinator.py and candidate_harness.py were separately read in full, with no execution by this reviewer yet. They maintain fixed trusted launch, A01 candidate preparation/execution, single-use intent, request barrier, finite deadline, protected logs and artifact/delivery checks. On revoke, additionally inspect final authoritative assignment revoked, workspace stopped and work package paused. Existing harness receipts alone do not explicitly assert those three final state fields.

All work remained read-only for repository/product files.
