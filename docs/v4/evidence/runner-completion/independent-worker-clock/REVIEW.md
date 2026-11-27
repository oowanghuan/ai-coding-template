# Corrected independent Worker clock review

The previous review of Worker 5a3c1dc56e43dae305f87a8fcbe948379954d59b52a0fe07d310ab49e0895acc incorrectly treated macOS Python 3.9 monotonic_ns observations as comparable across processes. That comparability claim is withdrawn. The prior records remain historical, not passing overlap evidence.

Python 3.10 documentation explicitly records that macOS time.monotonic became system-wide in 3.10; monotonic_ns has the same semantics. Source: https://docs.python.org/3.10/library/time.html#time.monotonic .

Replacement Worker SHA256: 05188893d5f9d87f3bd9d7c44e3e82be8c7c53293d538c02742fd8204dfee97d. Full source read: uses time.clock_gettime_ns(time.CLOCK_MONOTONIC) directly for start after stdin job read and finish after file write, emits clock name and actual PID, adds no new command/parameter/write permission. This fixed hash is approved for the previously bounded trusted-driver test arrangement.

Actual A01 verification: four fixed Worker processes. Two started only after previous completion have disjoint intervals; two started together have overlapping measured execution intervals. Every child start/end lies between parent-side reads of the same OS clock, PID matches the live child, file bytes match and process exit is zero. Source hash matched before and after. Raw observations, commands, profile hash and log bytes are retained alongside this review.

This validates clock comparability for the observed local environment and the positive/negative interval controls. It is not the external launcher integration, cross-host clock synchronization, or an independent general-purpose engineering evidence attestation. That integration must bind actual log fingerprints and PIDs to trusted driver receipts and reject the serial negative control.
