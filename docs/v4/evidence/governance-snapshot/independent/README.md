# Independent locked-baseline verification

This non-author execution checks the narrowed semantics requested by
[Advisor 7226757604](https://github.com/oowanghuan/ai-coding-template/issues/3#issuecomment-7226757604).
It reuses the reviewed author test design, with a newly created temporary Git
repository, candidate directory and protected governance records. It does not
claim an independently designed test suite or a new collector execution.

The exact product inputs match commit
`9df70b506dc109f3d4ff0d65332eefae0fff359d`: see
[seven-file binding](commit-binding.json). The frozen trusted coordinator is
`e941a7ec74bc1fbd5818181fed75b84037fadb467194841405594249e2963137`;
the separately pinned input manifest is
`c493ff5cf69e942c2cd020f5c8babcf1f8c6a5fa35a5a2072afc0527d866d5cf`.

## Actual execution

[Invocation](run/execute-invocation.json) records the run at
2026-11-27 20:03:17–20:03:19 UTC, exit 0. The
[summary](run/summary.json) records `passed: true`.

- Eleven actual local Git commands initialized `refs/heads/main`, committed its
  baseline and then committed a real change. The coordinator observed
  `b0d627cfbcb3413ac2d1880dff705a07ef2c5aae` advance to
  `a6c60c2c40b9ef06bd951db10e50b13134207467`, whose parent is the baseline.
  [Commands](run/git-operations.json) and both raw commit bodies are retained.
  Deterministic fixture contents and dates produce the same commit IDs as the
  author's test; the Git directory and execution are new.
- One public quality CLI invocation revalidated previously collected real
  evidence. Three public governance CLI invocations ran under Seatbelt:
  [before](run/verify-before.json), [after with identical inputs](run/verify-after-same-inputs.json),
  and [separate changed descriptor](run/verify-new-target-descriptor.json).
  There were **zero new collector executions**. The original quality evidence
  comes from the earlier [author governance chain](../../quality-governance/governance-author/README.md).
- Before and after the ref movement, the full governance decision was identical:
  `effective`, `verification_scope: locked_baseline`,
  `current_target_status: not_observed`. The original review, signoff, policy,
  candidate, existing protected files and seven product inputs remained byte
  identical. The changed descriptor alone was rejected with exactly
  `target-base-changed-recheck-required` and the same scope limitation.
- The independent reviewer recomputed all three `decision_id` values from their
  complete output bodies and checked the scope fields were included. Static
  review also verified that normal and handled-error verify paths carry both
  fields before the decision fingerprint is computed.
- Eight actual [boundary checks](run/canary.json) passed: protected writes and
  hardlinks, candidate-root removal, target Git reads, outside/checkout writes
  and networking were denied, and the explicitly provided environment contained
  no credential variables. These checks do not replace the broader prior A01
  process-information tests.

## Review conclusions and limits

The implementation now describes a locked snapshot consistently in the result,
CLI help, protocol, example and current acceptance statements. It does **not**
observe the live target. The coordinator's Git observations are test evidence,
not an input observed by the product. `effective` and exit 0 are not current-target
validation, merge permission or project acceptance. Live-ref observation,
freshness and merge-time concurrent-update checks remain unimplemented/unverified.

Protected principals, reviews and contract records are synthetic fixtures. This
execution does not certify real reviewer identity, Owner authorization or the
adequacy of the old test plan. The 32 governance unit tests in the accompanying
author evidence were not independently rerun here. The author's first fixture
attempt failed schema validation; that retained failure is not counted as a
passing run. This independent execution used the reviewed corrected fixture.

The host coordinator imports no candidate module. It invokes candidate CLIs only
inside the fixed A01 profile, with no network or checkout writes. Its host reads
of candidate files use bounded, single-link regular-file checks and no-follow
directory descriptors. Original files remain outside the repository.
[Export manifest](export-manifest.json) lists each original and public-copy hash
separately. Absolute machine paths are redacted; internal pins remain original
values, so these public copies must not be represented as unchanged runnable
originals. No product file was edited by this reviewer.
