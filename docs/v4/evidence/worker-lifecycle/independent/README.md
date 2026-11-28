# Independent OD09 checks

These checks were executed by the boundary reviewer, who did not implement the adapter, recovery, lifecycle, or demo product code. Reusing author test cases is disclosed: the independent work uses a new A01 execution directory and new synthetic projects/processes. This is **not real Claude/Codex model execution or engineering acceptance**.

## Current results

| Check | Actual result | Evidence |
| --- | --- | --- |
| Outer A01 boundary | Six fixed probes passed: trusted/outside/checkout writes or reads, hardlink alias, network, credential environment | `tests/canary-result.json`, `tests/canary.stdout.log`, `tests/profile.sb` |
| Adapter unit suite | 53 passed, zero skipped; inputs unchanged | `tests/adapters-result.json`, `tests/adapters.stderr.log` |
| Recovery unit suite | 26 passed, zero skipped; inputs unchanged | `tests/recovery-result.json`, `tests/recovery.stderr.log` |
| Initial combined lifecycle suite | Harness killed the test parent after 120 seconds; first harness failed to persist partial streams. No passing result claimed. | `tests/lifecycle-result-01.json` |
| Second combined lifecycle suite | 27 passed in 142.409 seconds, but repository source changed during the run. Diagnostic result only; not bound to a frozen revision. | `tests/lifecycle-result-02.json`, `tests/lifecycle-02.stderr.log` |
| Final combined lifecycle suite | 29 passed, zero skipped, 163.889 seconds. All tested framework/schema/fixture/test inputs unchanged. The only broad-manifest change was creation of the unused helper script; original broad result remains false. | `tests/lifecycle-result-03.json`, `tests/lifecycle-scope-assessment.json`, `tests/lifecycle-03.stderr.log` |
| Independent synthetic process demo | Two tests passed in 23.379 seconds; inputs unchanged. Actual separate child processes, Git worktrees, quota injection, confirmed stop, checkpoint, handoff, and one logical delivery. | `tests/worker_demo-result-02.json`, `tests/worker_demo-02.stderr.log` |

The demo uses a fixed synthetic supervisor and synthetic provider classification. It neither invokes a real model nor proves native provider tool isolation or an installed continuous scheduler. The enclosing A01 policy is the execution boundary; an environment flag alone is not evidence of sandboxing. The final combined-suite scope is explicitly assessed without overwriting the earlier broad manifest observation.

## Reviewed one-command helper

The reviewer inspected exact helper SHA256 `ea4b7505c3a0665278a3278b6661492c5930e943aefc2c5d6e2943530eefc337` before execution, and the Project Lead separately authorized that fixed copy. The helper was copied outside the checkout and executed with system Python `-I -B -S`, using existing installed dependencies without package installation. It imported only standard-library code on the host, froze source/dependencies into a new protected T tree, and executed the fixed demo only under the generated A01 profile.

The independent new fixture passed eight boundary canaries before demo execution and finished with exit zero and unchanged frozen inputs. Actual parallel synthetic workers, exit -15 of the interrupted writer, checkpoint restoration, token 1 → 2, old-token rejection, recovery to the worker pool, and exactly one logical delivery each for WP-A/WP-B were recorded. PMO and provider model calls were both zero. See `helper/run/result.json`, `helper/run/stdout.log`, `helper/demo/journal.json`, and `helper/demo/final-state.json`. The helper's `passed` field denotes this bounded demonstration, not engineering acceptance. System Python attempted denied xcrun cache writes outside C; those warnings remain in `helper/run/stderr.log` and did not require a permission exception.

`REVIEW-INPUTS.json` gives the exact 36 product/test inputs for later Git blob binding. This review does not claim universal recovery: the positive path begins with a registered running process; prepared/finished work with preserved output but no owned process-stop proof remains fail-closed and needs trusted reconciliation.

## Official CLI investigation

Fixed installed binaries were identified by SHA256. Official help, offline schema generation and login-status commands did not request model inference. Authentication diagnostics remain outside the repository; `cli-metadata/status-summary.json` contains only the explicitly safe findings. A positive login status does not prove available quota or successful inference.

- Claude 2.1.332: local managed-policy sources were absent at inspection, but that does not establish absence of server-delivered policy. In the exact clean environment with `--safe-mode --restricted --setting-sources ''`, the official read-only doctor exited zero and reported remote settings not fetched because usable credentials were unavailable. Official auth status returned `loggedIn=false`. No login, token copying, or new API was attempted.
- Codex 0.169.0: official login status observed ChatGPT authentication. Offline `app-server generate-json-schema --experimental` produced 479 schemas. `ThreadStartParams` accepts a named permissions profile; its legacy `readOnly` sandbox policy does not itself carry readable-root restrictions. No blanket tool-disable field was found in the generated request schemas; this is a limited schema observation, not a claim that every possible embedding API lacks such a feature.

Official references: [Claude CLI commands](https://code.claude.com/docs/en/cli-reference), [Claude read-only doctor and updates](https://code.claude.com/docs/en/setup), [server-managed settings](https://code.claude.com/docs/en/server-managed-settings), [Codex permissions](https://learn.chatgpt.com/docs/permissions), [Codex authentication](https://learn.chatgpt.com/docs/auth), [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Codex native boundary: partial success, failed overall admission

A new temporary HOME and named permission profile denied the filesystem root, granted minimal runtime reads and a public fixture directory, denied a synthetic trusted directory, and disabled command networking. Only fixed system probes executed; no repository module, candidate CLI implementation, or model was run.

1. Initial system Python shim could not locate developer tools within the restricted read roots. This failure is preserved in `codex-native/result.json` and `stderr.log`. The next run used the fixed installed Command Line Tools Python and explicitly granted its runtime read directory.
2. Native sandbox then allowed public fixture reads and own writes; synthetic trusted-file reads/writes and localhost connection attempts returned EPERM. The synthetic trusted file was unchanged (`codex-native/result-02.json`, `stdout-02.log`).
3. This was insufficient for A01: after an owned synthetic Python process emitted a readiness marker, both the host baseline and the native-sandbox probe could read that process's synthetic environment marker through `KERN_PROCARGS2`. No actual credential or unrelated process was queried (`codex-native/procargs-result-02.json`). The earlier sleep-based probe lacked a readiness handshake and returned no marker despite a successful syscall; it is preserved and is **not** counted as a denied read.
4. An independently approved experiment added only `deny process-info* (target others)` around the trusted official CLI, retaining its native inner filesystem/network sandbox. Nested application failed with exit 71 and `sandbox_apply: Operation not permitted`; the system probe did not execute (`codex-layered/result.json`, `stderr.log`). No unsandboxed fallback was attempted.

Therefore this version's tested native command profile has useful filesystem/network isolation, but the tested configurations do not yet meet the complete A01 boundary. No real-provider acceptance is claimed. A future reviewed launcher needs a demonstrable boundary for all enabled execution/read tools; prompt instructions are not that boundary.

## Provenance and limitations

`FILE-MANIFEST.json` records raw and public-copy SHA256 separately. Machine-specific paths are replaced in public copies; these copies are review artifacts, not directly executable scripts. Original logs, policies and exact commands remain outside the repository. Authentication/doctor raw logs are intentionally excluded; their original byte fingerprints are retained. Safe summaries and this reviewer-authored report are explanatory artifacts rather than original execution output.

A01 protects candidate execution from credentials, external network access and checkout writes. It does not make candidate-authored assertions independently authenticated, and these tests do not claim resistance to a malicious machine owner, arbitrary descendant-process escape, or any cloud provider integration.

## Advisor supplement: completed delivery recovery replay

The reviewer inspected the new test SHA256 `bea33bd6d36eec6e5d40192ffcdd03ff503db6e34e3cdead3027002d42ae4d29`, then executed only that test in a new independent T/C fixture. Six A01 boundary probes passed first. The single test passed in 24.949 seconds with all measured inputs unchanged; the earlier suites and their original artifacts were not rerun or rewritten.

After three real fixed writer starts and completed synthetic deliveries, the test reopened the Store from disk and replayed the successful recovery operation twice with its original ID and payload. Both returned the original receipt. Authority bytes, every workspace file hash, assignment/delivery state and the original demo journal remained unchanged. Reusing the same probe under a new operation ID was rejected as stale/unknown. A fail-on-call Popen observer existed only in the post-completion window and observed no new start attempts; it did not replace the three preceding real processes. See `completed-recovery/runner/result.json`, `completed-recovery/runner/stderr.log`, `completed-recovery/observed-result.json`, and `completed-recovery/demo/`.

This verifies the concrete local fixture's duplicate recovery behavior. Real provider/API calls remain zero; it does not certify exactly-once effects across external services or all possible recovery operations.
