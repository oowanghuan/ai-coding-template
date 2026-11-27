# Independent boundary review — WP-102 finite external launcher

Reviewed source: driver SHA256 `cfb917f6b039ec3de24bcc2c6c41fba314cb3945d4cb01387b311e0f1f2db2ce`; fixed Worker SHA256 `62d4f9a63ec66945965e8d874baf7d9f6f3bab5956990be44dcf8c22ba00804c`.

Decision: this exact driver and fixed Worker may be copied to protected trusted storage for a finite synthetic integration batch. This is permission within the existing WP-102 implementation boundary, not phase acceptance. Controller must remain inside A01; trusted config/program/receipts must remain outside candidate writable storage; candidate root must be explicitly protected against unlink, rename and replacement; configuration and copied programs must be fingerprinted before execution. No arbitrary command, model, credential, network, release or persistent service is included.

Reviewed implementation: strict finite job capabilities; fixed program and environment; bounded fd-pinned mailbox reads; immutable configuration byte hash in receipts; fixed content/job/operation binding; per-worker Seatbelt; output intersection with stable candidate anchor; nonblocking bounded stdin; timeout/cancel only against owned live Popen; prior launching/running becomes unknown; no stale-PID signal/relaunch; observed exit and log hashes before terminal receipt. Project state remains sole task authority. Nonoverlapping workspaces are checked.

Findings resolved before this decision:
- Blocking stdin could defeat timeout supervision: changed to nonblocking per-tick writes, tested with real unconsumed pipe and Fake process.
- Parent nonwritability did not preserve candidate root: deployment now requires explicit root unlink/rename prohibition and actual canary.
- Workspace ancestor symlink race could redirect policy: output is intersected with stable candidate root, workspace read grant removed, actual outside-root substitution canary checked.
- Nested workspace configurations now rejected.
- External client receipt must bind exact config bytes; unknown cancel outcome must preserve unresolved state. Latest client does so. Timing type alignment was sent to root.

Independent execution: `result.json`, `stdout.log`, `stderr.log` record 24 passing pure/Fake launcher tests under A01, exit 0, matching source hashes before/after. This does not prove a real Worker launch or overlap.

Additional parent-run raw evidence read independently:
- `<FIXTURE>/external-boundary-canary/result-final.json`: T direct write and T-to-C hardlink denied; no alias write claimed.
- `<ANCHOR_FIXED>/result.json`: rename and empty-root removal denied; child write allowed.
- `<OUTPUT_BOUNDARY>/result.json`: normal output write allowed/read denied; post-policy-generation ancestor substitution outside C denies read/write and preserves victim.

Open acceptance items: real external backend chain, genuine overlapping Worker intervals, cancellation/revocation and unknown reconciliation, immutable submitted delivery and replay behavior. Existing nested direct backend failure remains a documented limitation; do not relabel its skipped success cases as passing.
