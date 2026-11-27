# WP-103 independent CLI journey review

Result: 42 assertions across 27 real public CLI/Git commands passed, process exit 0. No skipped scenario. The inspected author harness was independently executed in a new disposable target under A01; this is independent execution of the same test design, not an independently invented full acceptance suite.

Inputs: 181 old files were verified against Git blobs at f95b03ab733fd45ed480aba162fee1943ea58c43. New snapshot adds only the exact five overlay files in input-manifest.json; all five matched current working files when copied. Parallel external-launcher changes were excluded. Both input snapshots remained byte-identical after execution.

Executed journeys: fresh init and dirty existing Git import using 0.2.0-preview; upgrade using 0.2.1-preview; new immutable guide selection; old guide and task authority preservation; old/new public CLI readability before/after upgrade; idempotent repeated apply; rollback and repeated rollback; original tracked dirty work, untracked files, native AGENTS/CLAUDE rules and Git bytes preserved. Cross-version upgrade changed the installed guide, not authority protocol version.

Isolation: outside read/write, checkout write, both snapshot writes and network were actually denied; credential environment was absent. Raw command arguments, exit codes, stdout/stderr and fingerprints are in cross-version-result.json and commands/. Environment/profile/harness fingerprints are in result.json. These are local synthetic filesystem/Git checks, not cloud/provider integration or a general migration proof.

No product or repository files were modified by this reviewer.
