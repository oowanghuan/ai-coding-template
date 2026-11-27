# WP-203 author verification: real quality evidence and governance CLI

This batch executed five real collector runs and 17 real CLI invocations under
the reviewed A01 boundary. All 17 CLI outcomes matched their expected semantics:
three quality Gates passed, two quality Gates failed as designed, and twelve
governance decisions correctly accepted or rejected the fixture signoffs.
It is author verification, not independent acceptance or Owner phase approval.

The protected reviewer/acceptor/Owner principals are explicitly synthetic test
identities. Quality tests actually executed; identity fixtures are not a claim that
real people reviewed the product. Governance's explicit evaluation clock was the
fixture value `2026-11-27T23:00:00Z`; actual wall-clock execution times are retained
separately in the command records.

## Results and evidence

| Scenario | Observed result | Record |
| --- | --- | --- |
| Real passed Gate → protected review/signoff | effective, exit 0 | [positive](experiment/stage/05-positive.json) |
| Same tree, different exact commit | effective, both commits retained | [same tree](experiment/stage/06-same-tree-new-commit.json) |
| Preapproved exact GUIDE byte transformation + new actual Gate | effective | [mechanical](experiment/stage/07-mechanical-exact.json) |
| Changed target base | rejected, exit 2 | [base](experiment/stage/08-target-base-changed.json) |
| Changed governing contract | old signoff rejected | [changed](experiment/stage/09-contract-changed.json) |
| Restored old contract content/version | old signoff still rejected | [restored](experiment/stage/10-contract-restored-old-signoff.json) |
| Fresh collector execution, then new review/signoff | effective | [new collector](experiment/stage/fresh-success-collector.json), [new Gate](experiment/stage/11-quality-fresh-success.json), [new signoff](experiment/stage/12-fresh-review-after-restore.json) |
| Explicit revocation | rejected | [revoked](experiment/stage/13-revoked.json) |
| Unexpired deviation | effective with active deviation retained | [active](experiment/stage/14-deviation-active.json) |
| Expired deviation | rejected | [expired](experiment/stage/15-deviation-expired.json) |
| Exact subject/scope closure backed by a real passed Gate | effective | [closed](experiment/stage/16-deviation-closed.json) |
| Actual baseline/current failures | known=`known`, new=`new`; still rejected | [comparison](experiment/stage/17-baseline-known-new-no-waiver.json) |

The fresh collector ran **after** the contract-change and contract-restoration
rejections. It used a new run ID and new evidence/Gate against the same exact Git
subject; the later review and signoff bound those new records. It did not reuse
old evidence while claiming to have rerun the tests.

The baseline and current runs use the same executable entrypoint, environment and
case definitions. An auxiliary data-file change produces a second failure. The
existing failing case retains its exit and output fingerprints. Neither the
baseline reference nor the remediation plan turns the failed Gate green.

[Summary](experiment/stage/summary.json), [prepared input bindings](experiment/stage/prepared.json),
[coordinator](experiment/stage/coordinator.py.txt), and the complete trusted
plans/source snapshots/collector receipts/logs under `experiment/trusted/` allow
inspection of the actual chain. The real engineering entrypoints are finite
synthetic checks, not a complete test suite for the framework itself.

## Unit and public CLI checks

The frozen governance suite ran **28 tests, 28 passed, 0 skipped**, subprocess exit
0. [Recorded command/environment/source hashes](unit/frozen-result.json) and
[full test log](unit/frozen-stderr.log) cover wrong SHA/tree, unauthorized or forged
source, high-risk self-review, missing dependencies, stale history, revocation,
restoration, expired deviations, mechanical deltas and real CLI inspection.
Successful Gate objects in unit tests are explicitly synthetic; the real Gate
chain is the separate integration experiment above.

The initial run failed because ordinary directory opens needed ancestor directory
read permission. A second attempt briefly added two literal directory-read grants.
Those grants were withdrawn; both [initial failure](unit/run-1.log) and
[intermediate log](unit/run-2.log) are preserved. The final reader uses Darwin
O_SEARCH. Its [final sandbox](unit/hardened-profile.sb) also denies other-process
information and omits broad sysctl-read authorization. Earlier profiles are not
proof of credential isolation merely because child environment variables were
cleared. The frozen run and real experiment use the hardened boundary.

## Pins, redaction and limits

- Approved real collector: `f4ad7874c7dc9415f4dc0d1d26f2d4d095b42ef7580b786152f0886452d9ab6f`.
- Approved coordinator: `49500acc7bef672cbcbb9a070b138897ee3d00ec38ad386da17f11a1ff946131`.
- All prepared product/source/plan inputs remained unchanged through execution.
- [INDEX.json](INDEX.json) separates original raw-file SHA-256 from public-copy
  SHA-256 and gives logical source locations. Absolute workstation paths are
  replaced by placeholders. Embedded pins still describe the original bytes;
  the redacted bundle must not be replayed as an authenticated original bundle.
- Reproduction requires a reviewed coordinator, pinned collector and a **new**
  isolated experiment. Existing execute intent prevents overwriting this run.
- No network, external service, paid model or real project task was involved.
  No task authority, merge, deployment or business milestone was advanced.
- The fixture is cooperative. Protected-source authenticity relies on the reviewed
  operator and OS write boundary; this is not PKI or hostile-host-owner protection.
  A finite test plan does not establish product-wide test completeness.
