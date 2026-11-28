# Independent continuation-candidate review

The non-author reviewer read the candidate continuation module, the minimal poll integration, the unchanged notification bridge, and the fake-transport tests. Three issues identified during review were corrected before this run:

1. Changing the public batch ID could reset both the activation budget and the no-progress allowance. The protected registration now caps all retained activations across batches; the same work item and progress fingerprint retain their two-activation limit across batch changes.
2. Only recognized pending Advisor/Owner events were blocking continuation. A registered fingerprint of the foreground-read Owner comment set now detects added, edited or deleted Owner comments, including unrecognized pause/revocation text, and requires foreground reconciliation. This is a read cache, not a new authorization source or a per-step approval requirement.
3. Default JSON parsing accepted contradictory duplicate keys in the remote ready fragment. The parser now rejects duplicates, including nested progress fields.

The final candidate was copied into a new protected source directory and executed only inside a new A01 fixture. Six real boundary canaries passed before the test suite. All **41 tests passed in 0.142 seconds**, zero skipped, exit zero; all six copied Python inputs remained unchanged. This independently reran the author's test design. Native IPC and GitHub calls were fake; guards prohibit real native clients and unexpected APIs. The production `poll.py` and `session_delivery.py` hashes were measured before and after and remained identical.

The reviewed core hash is `cbceee49b729f89730de517e69df3211e6bf559eb5dd5bf77ef6a7521caaebc8`; the candidate poll hash is `1a864763d010c9452caab186d653e276ab1797e8d417f30140afac32b8a5e514`. `input-manifest.json` identifies all six candidate/test byte inputs. These are operational candidate files, not an assertion that the production broker imports them.

## Review conclusion

The candidate may proceed to joint design review. It reads the existing remote work-package document as its task authority, preserves the existing broker lock, defers continuation while the bound session is active/unloaded or other queue entries exist, and never uses steering, session creation, permission changes or model selection for a continuation. Unknown queue/start outcomes are reconciled read-only; model acknowledgement is distinct from progress or completion. Expiry, cooldown, persistent budgets and unchanged-progress limits prevent unbounded self-triggering. The local configuration and receipts do not create another task ledger.

This is **not deployment or live wake-up acceptance**. No genuine bound session ID or binding file was read into the test fixture or copied into this public package. All tested IDs are explicit synthetic fixtures. No model inference, real queue write, live GitHub write, launchd change or new service occurred.

The native interface lacks an atomic idle precondition. An idle-to-active race after a known queue add can leave the notification queued; the candidate preserves it and does not steer or explicitly start it while busy. It cannot claim that a single-instance file lock also locks the application's session state. Changed authority, unknown delivery, or an exhausted budget requires reconciliation rather than blind retries. Actual same-loaded-session delivery, model receipt, useful work and restart recovery remain to be demonstrated before any claim of continuous production operation.

`result.json` records the actual sandbox invocation, environment, timestamps, input hashes and production code hashes. `stderr.log` contains the full unittest summary. `FILE-MANIFEST.json` separates original and public-copy hashes; machine paths are replaced in public copies, while raw artifacts remain outside the repository. Source copies are provided in the separate author package; this package does not duplicate a real production configuration.
