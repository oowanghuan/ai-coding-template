# CLI and official-protocol inventory — 2026-11-27

Trusted installed native CLI metadata probes subsequently succeeded with existing host permissions in a new candidate-free temporary directory, clean HOME, and no API/GitHub/SSH credential environment: all five fixed `--version`, `--help`, and Codex `exec --help` invocations exited 0. Actual version output was Codex 0.169.0 and Claude Code 2.1.332. Binary hashes, commands, output hashes and the temporary file inventory were recorded outside the repository. No model, auth/login, doctor, update or credential operation was called.

An earlier attempt under the unchanged Python-oriented A01 profile aborted before help (Codex -6 guard-page EINVAL; Claude -5 Bun startup trap). This is evidence that that profile is incompatible with their startup, not that either provider is unavailable. No permissions were widened for candidate code. Candidate adapter tests still run under A01, while executing fixed official metadata commands follows their separately reviewed trusted-tool boundary. Successful help does not validate live model isolation, managed customization suppression or the entire proposed argument combination. Raw failures are retained; machine-specific crash-report links are not public product evidence.

Official documentation is a separate source from local runtime compatibility:

- Codex `exec --json` emits event records including terminal success/failure. The current exec source exposes an error message without the app-server typed cause. Message prose cannot safely distinguish quota, authentication or context exhaustion. [Non-interactive guide](https://learn.chatgpt.com/docs/non-interactive-mode), [official exec event source](https://github.com/openai/codex/blob/main/codex-rs/exec/src/exec_events.rs).
- The app-server protocol provides typed `codexErrorInfo`, distinguishing usage limits, rate limits, context exhaustion, unauthorized access and session budgets. A retrying notification does not mean the turn stopped. This parser supports the documented event shape as an interface; it does not start app-server. [App-server reference](https://learn.chatgpt.com/docs/app-server), [official error translation](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/error.rs).
- Claude rate-limit events identify rejected limits and optional epoch reset time; `credits_required` explicitly identifies exhausted included usage requiring credits. Per-invocation cost budgets and explicit authentication errors are separate; a maximum-turns stop is not project budget exhaustion. A generic billing or invalid-request message is not sufficient to infer quota or context. [Agent SDK reference](https://code.claude.com/docs/en/agent-sdk/typescript).
- Claude built-in tool restrictions alone do not disable MCP. Safe-mode retains managed policy; restricted mode and configuration flags are version-dependent. Codex read-only restricts writes and is not a no-tools boundary. Generated argv is therefore only a disabled planning template pending exact installed-version validation. [Claude CLI reference](https://code.claude.com/docs/en/cli-reference), [Codex command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli).

The online references may evolve independently of the installed binaries. Fixtures encode the explicitly documented shapes and remain labelled synthetic. Missing signals return conservative error, and missing reset time stays null. This work does not claim live provider authentication, quota recovery, paid access or cloud compatibility.

## Bounded follow-up — 2026-11-28

The installed Codex version remains 0.169.0. Its actual sandbox help uses the
flat command form; the public manual's `sandbox macos --help` example attempted
to execute the literal `macos` and failed with execvp/exit 71. This metadata
failure is separate from the earlier nested-sandbox `sandbox_apply` failure.
No unchanged failed isolation experiment was rerun.

Version-matched public source review found separate registration and enforcement
paths for command, patch, image, MCP, extension and other tools. Disabling shell
alone does not establish a closed tool surface; this is not evidence that the
remaining file tools bypass their permission policies. Effective configuration
and runtime admission remain unverified. Matching a release tag name to a
version string is not installed-binary build attestation.

The exact restricted Claude 2.1.332 auth-status invocation again returned
`loggedIn=false` (exit 1), without login, token copying or inference. This does
not imply the account has no subscription or that every other environment lacks
authentication. See the [native admission report](../docs/v4/evidence/native-admission/README.md)
for safe metadata, independently reviewed source findings and concrete unblock
conditions. Native live admission remains blocked; approved synthetic recovery
work can proceed independently.
