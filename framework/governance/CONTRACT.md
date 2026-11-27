# Local governance interface 1 (WP-203)

Governance reads versioned records and computes decisions. It does not schedule,
claim, merge, accept a Work Package, or duplicate the task state machine. The
reviewed operator provisions an OS-protected T and pins the trust-file hash out of
band; candidate C must not write/rename T or its ancestors. A caller-provided
principal, different model, directory name or self-computed hash is not identity.
The initial implementation assumes this protected operator boundary; it is not PKI
or protection against a hostile machine owner.

## Public API / CLI

`framework.governance.evaluate.verify_bundle(trust_path, expected_trust_sha256,
signoff_id, candidate_path, at)` reads only registered protected records and calls
`framework.quality.gate.verify_bundle` with the quality trust path/hash/run fixed
by the governance trust configuration. It never accepts serialized caller
`status: passed` JSON. `at` is explicit UTC (`YYYY-MM-DDTHH:MM:SSZ`).

Result: `format: governance-decision/1`, `status:
effective|rejected|unverifiable`, sorted `reasons`, `decision_id`, `signoff_id`,
`review_id`, `wp_id`, `wp_revision`, `reviewed_subject`, `candidate_subject`,
`target_base_sha`, `gate_id`, `candidate_gate_id`, `equivalence`,
`active_deviations`, `failure_analysis`, `invalidated_signoffs`,
`ledger_tip`, `trust_sha256`, `verification_scope: locked_baseline`,
`current_target_status: not_observed`. These scope fields are present on every
verify outcome, including rejected/unverifiable, and are bound by `decision_id`.
No task/merge/deploy/business milestone is inferred.

`effective` means the pinned signoff applies under the supplied locked-baseline
snapshot at the explicit evaluation time. This verifier does not observe a live
Git target ref, fetch a remote branch or determine whether its head has advanced.
If review, candidate and protected policy all retain the same old target SHA, the
result may remain `effective` even after the real target moves. It is **not** a
current-target validity assertion or a merge-time safety check. The status and
exit code remain compatible; consumers must retain the scope limitation.

CLI `scripts/v4_governance.py verify --trust PATH --trust-sha256 HASH
--signoff ID --candidate PATH --at UTC`. `inspect` / `export` read the same pinned
ledger. `impact --changed-contract ID` computes transitive dependents.
`append-proposal --source-id ID` emits a new hash-chained ledger proposal and tip;
it never overwrites the protected ledger or authenticates its own proposal.
A reviewed operator must append/pin it outside candidate write authority.

## Protected trust file

```
format: governance-trust/1
trusted_root, candidate_root: disjoint canonical absolute directories
project_id
ledger: {path, sha256, sequence, head_sha256}
sources: {source_id: {path, sha256, principal, role, context_id, independence_group}}
work_packages: {wp_id: {revision, risk, author_principals, author_contexts,
                       author_groups, required_paths, target_base_sha,
                       allow_same_tree_commit, separate_acceptor, required_contracts,
                       mechanical_changes:{path:{old:entry|null,new:entry|null}}}}
contracts: {contract_id: {depends_on: [contract_id]}}
graph_complete: bool
quality: {trust_path, trust_sha256}
```

These are read-only policy/identity/object bindings imported from project
management, not a second task authority. Sources and ledger are registered paths
inside T. Source `role` is `contract_owner|reviewer|acceptor|owner`; principal,
context and independence group come from this configuration, not record claims.
The protected ledger sequence and exact tip prevent an old Git export from
removing a revocation or restoring an invalidated signoff.

## Ledger and source records

Ledger: `{format: governance-ledger/1, project_id, entries: [...]}`.
Each entry is `{sequence, source_id, source_sha256, previous_sha256, entry_sha256}`;
`entry_sha256` hashes canonical JSON of the other fields. Sequence starts at 1,
previous hash starts at 64 zeroes. Sources are immutable raw-byte-hash-pinned JSON:
`{format: governance-record/1, kind, issued_at, payload}`.

Kinds / payloads:

- `contract`: `{id,path,version,sha256,depends_on}`; versions append. A contract
  update invalidates earlier affected signoffs transitively, permanently. Restoring
  an earlier byte/version cannot reactivate them; a new review/signoff is required.
- `review`: `{id,wp_id,wp_revision,subject,commit_object,target_base_sha,paths,
  contract_refs:[{id,version,sha256}],quality_run_id,conclusion,summary,
  deviation_refs,policy_sha256}`; subject is quality's `{commit,tree,manifest_sha256}`.
  Conclusion is `approved|changes_requested` and summary must be nonempty.
  `policy_sha256` is the canonical hash of this WP’s protected policy. Policy
  changes require a new review; caller-selected policy cannot expand a prior review.
- `signoff`: `{id,review_id,gate_id,evidence_sha256}`. The source must be an
  independent authorized acceptor, and the current real Gate must match exactly.
- `revoke`: `{signoff_id,reason}`; source is owner or the original acceptor.
  Revocation is monotonic history, never undone by later content restoration.
- `deviation`: `{id,revision,wp_id,wp_revision,subject_commit,scope_paths,reason,
  expires_at,status,closure,baseline}`; status `open|remediation_planned|closed`.
  `closure` is null or `{quality_run_id,gate_id,subject,scope_paths}`. `baseline` is
  null or `{quality_run_id,subject}`. A plan is not closure. Closed records require
  the real protected closure Gate to pass against the exact reviewed subject, WP
  revision, run and scope. Open records expire and remain visible as deviations.
  Active deviations never turn a failed quality Gate into passed.

A candidate is `{format: governance-candidate/1, wp_id, wp_revision, subject,
commit_object,target_base_sha,paths,quality_run_id}`. Raw Git commit-object SHA and
named tree must match. Normally candidate tree and manifest equal the reviewed/Gate
object. Different commit with the same tree is allowed only by pre-pinned policy,
with both exact commits retained in the decision (`equivalence: same_tree_commit`);
this does not pretend the new commit was itself tested. A changed target base
within the supplied snapshot requires new review. A live ref movement absent from
those inputs is not detected.

For a different tree, `quality_run_id` must identify a new actual passed Gate.
The complete manifest delta must equal protected `mechanical_changes`, with every
old/new entry `{sha256,mode: "100644"|"100755"}` or null for absence. Every changed
path must be within the signed scope. Additional, missing, or differently transformed
files fail. The policy must already be covered by `review.policy_sha256`; it cannot
be added after signing. This minimal mechanism does not classify arbitrary changes
as mechanically harmless.

`failure_analysis` compares a protected, exactly bound baseline Gate (passed or
failed, never unverifiable) with the current Gate. A known failure requires the
same case definition, entrypoint content/mode, environment, exit/signal/timeout and
stdout/stderr fingerprints and lengths. Other current failures are new. The result
is diagnostic: there is no baseline waiver path that makes a failed Gate effective.
The full product-completeness of test definitions is outside this finite adapter.

A complete pinned dependency graph is required. Missing contracts/edges or unknown
impact is unverifiable, not an empty impact set. Review scopes must cover the pinned
required paths; contract references bind the registry versions used by that review.

## Operational boundary and reproducibility

`verify` exits 0 for effective within the locked snapshot, 2 for rejected, 3 for
unverifiable. Exit 0 does not establish the current live target or authorize merge. Other read-only
commands exit 3 for unverifiable and 0 for a verified result/proposal. A proposal
is explicitly `effective: false`; it needs a protected operator import and an
out-of-band updated trust pin. Duplicate source IDs and stale ledger tips fail.
No command writes authoritative state or revives prior signatures.

The trusted root encloses the governance files and quality trust/run roots; the
candidate descriptor is in disjoint C. Reads use no-follow directory descriptors
at every ancestor, single-link regular files, bounds and raw-byte hashes. On
Darwin O_SEARCH avoids granting directory-listing permission just to traverse.
The external caller must enforce T/ancestor write isolation, no network, no
credential reads, no process-environment reads, and no syscall credential leaks.
A clean child environment alone is not isolation. No hostile machine owner claim.

Unit tests label their injected Gate results as synthetic. A CLI verification of
actual engineering acceptance must additionally use a collector-produced protected
bundle and actual quality verifier; serialized test fixtures are not that evidence.
