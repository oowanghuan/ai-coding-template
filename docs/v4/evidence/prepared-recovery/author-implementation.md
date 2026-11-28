# WP302 implementation checkpoint

Four candidate files changed, not committed by author; no candidate execution on host.

- framework/local/store.py: optional strict execution_domain on claim/dispatch-next; general remains default; explicit direct-local-only generates immutable v4-direct-local- namespace. Only that namespace gets a versioned start receipt with credential, complete authorization and work-input bindings.
- framework/local/handoff.py: recover_prepared(root, credentials, actor, expected_revision, operation_id), an ordinary Store transaction. Requires unique modern start receipt, no durable run-begin for that workspace, final checkpoint/history/actual bytes, current authorization and input bindings. Fences old right and marks workspace stopped without inventing an exit or process-stop observation. Same intent replay is read-only; another operation is rejected after recovery.
- framework/local/external.py: direct constructor and run_external reject reserved workspace/target namespace before request/config side effects.
- framework/local/launch_driver.py: standalone fixed driver rejects every casefolded workspace/target path segment in this namespace; existing validation runs again before launch. This prevents an ancestor-workspace output from targeting the reserved domain.

Compatibility: legacy/default general workspaces retain existing execution behavior but cannot use the new automatic recovery. Old owned-Popen confirmation unchanged. No schema migration, no retrofit of missing proof, no arbitrary signal or PID absence inference.

Trust boundary: cooperative single-owner authority plus reviewed launchers; this is not a universal OS process absence claim. New trusted-driver bytes require independent review. Never hot-replace an armed legacy driver; before using the new domain, no older pinned driver may hold external authority over it. No external service, session, fee, permissions or infrastructure added.

Boundary reviewer and independent test author are reviewing/testing the same four frozen files. Independent tests own tests/lifecycle/test_unstarted_handoff.py. Root owns documents, evidence packaging and publication. Exact current source hashes sent to root and reviewers; git diff --check passed. No host execution of the changed driver has occurred.
