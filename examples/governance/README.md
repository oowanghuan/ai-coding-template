# Inspect and evaluate protected governance records

This example consumes an operator-provisioned bundle; it does not generate an
identity, authorize itself, or label synthetic fixture evidence as accepted.
Use the formats in [the governance contract](../../framework/governance/CONTRACT.md)
and [JSON Schema](../../schemas/governance.schema.json). The operator supplies the
trust SHA through a protected channel and keeps the ledger and quality runs outside
candidate write authority. The framework checkout is read-only during evaluation.

```sh
FRAMEWORK_ROOT=/path/to/ai-coding-template
TRUST=/protected/project/trust.json
TRUST_SHA256=<operator-supplied-64-hex-pin>
CANDIDATE=/candidate/project/candidate.json
AT=2026-11-27T20:00:00Z
python3 "$FRAMEWORK_ROOT/scripts/v4_governance.py" inspect \
  --trust "$TRUST" --trust-sha256 "$TRUST_SHA256" --at "$AT"
python3 "$FRAMEWORK_ROOT/scripts/v4_governance.py" impact \
  --trust "$TRUST" --trust-sha256 "$TRUST_SHA256" --at "$AT" \
  --changed-contract API
python3 "$FRAMEWORK_ROOT/scripts/v4_governance.py" verify \
  --trust "$TRUST" --trust-sha256 "$TRUST_SHA256" --at "$AT" \
  --signoff S1 --candidate "$CANDIDATE"
```

The commands themselves are read-only. Candidate execution belongs in the
reviewed A01 sandbox; a pasted shell command does not establish that sandbox.
Every verify result includes `verification_scope: locked_baseline` and
`current_target_status: not_observed`, including rejected or unverifiable results.
An effective result means this pinned signoff applies to the supplied locked
snapshot of candidate, policy and target-base SHA. It does not observe the live
Git target ref. If all those inputs still contain the old SHA after the real
target moves, verification can remain effective within that old snapshot.
Do not use this result as current-target validation or merge authorization.
It does not mean merged, deployed or business accepted.
A failed engineering Gate remains rejected even with an open deviation.

To propose a new immutable source, the operator first registers its protected
path/hash/principal/role/context/group in the trusted configuration. Then
`append-proposal --source-id NEW_SOURCE` prints a proposed next ledger and tip.
It writes nothing. Importing that proposal and distributing its new trust pin is
a separate trusted operator action, preserving the full current history.
`export` includes public governance records and should only be published after
checking their content; this tool does not declassify project data.

Tests in `tests/governance/test_governance.py` contain explicitly synthetic public
identities and Gate objects to exercise rejection semantics. Those fixtures are
not an operational protected trust configuration and cannot prove engineering
acceptance.
