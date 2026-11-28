# Continued-work pulse: review-stage operational prototype

This directory is a candidate only. Production `poll.py` / `session_delivery.py`, launchd, session binding, and live queues have not been modified. `config.example.json` is disabled and paused. No real model session/IPC/GitHub request has been made by these tests. This is not the finalized V4 product scheduler; the Owner's existing collaboration practice must inform that architecture.

## Authority and finite inputs

The sole task source remains the public repository's `docs/v4/V4_WORK_PACKAGES.md`, read through GitHub GET at the exact branch SHA. Local configuration contains only the branch, protective switches, expiry, cooldown, activation limits and a fingerprint of the Owner comments already read by the trusted foreground Project Lead. It contains no parallel task backlog or grant of authorization.

The candidate accepts exactly one block and rejects duplicate JSON keys, including nested objects:

````markdown
<!-- v4-continuation-ready:v1 -->
```json
{
  "version": 1,
  "batch_id": "example-paused",
  "scope_ref": "OD-09",
  "control": "paused",
  "expires_at": "2026-12-01T00:00:00Z",
  "activation_budget": 8,
  "items": [
    {
      "id": "WP-303-example",
      "wp_id": "WP-303",
      "status": "blocked",
      "depends_on": [],
      "progress": {
        "checkpoint": "example-only",
        "milestone": "await comparison with existing collaboration practice",
        "evidence_refs": []
      }
    }
  ]
}
```
<!-- /v4-continuation-ready -->
````

Only the already authorized OD-09 WP-301/302/303 scope is accepted. This refers to the existing conversational authorization; neither a transferred decision note nor this JSON is a new Owner ruling. A future scope needs explicit adaptation/review. Documents can represent only the public Project Lead's recorded progress, not independent engineering verification. Updating a checkpoint field is not proof that tests or implementation completed.

## Dispatch behavior

- The candidate `poll.py` calls continuation inside the original single `poll.lock`, including rounds with zero new Advisor comments. Existing Advisor/Owner events take precedence. Unresolved broker writes remain explicitly blocked for foreground reconciliation.
- Missing/disabled config, local pause, public pause/block, expiry, dependency not done, non-ready tasks, exhausted budget or an existing queue stop dispatch with a recorded reason. A new, edited or removed Owner-account comment in Issue #3 changes the cached ledger fingerprint and blocks until Project Lead reconciles it and refreshes the read cache. This does not interpret arbitrary prose as a machine-understood revocation or grant; it requires foreground reconciliation without a new Owner comment. Recognized Advisor/Owner events still use the original channel first. A new session is never created or resumed; only the bound loaded thread with the matching cwd is used.
- An observed active thread receives no continuation steer or queue write. Immediately before adding and before starting a queue item, the thread, queue, branch and protective config are checked again.
- The native queue API has no `expectedIdle` / atomic idle precondition. A thread may become active between the check and add/start. If observed after add, preserve the queued item and do not steer/start. This is not a claim of atomic idle-only enqueue. A known successful add with no prior start attempt can later start once when it is the sole queued item and the original authority still matches.
- Save deterministic activation/client ID and intent before each write. Unknown add/start outcomes are reconciled only through history/queue/model ACK, never retried. A missing history row is not evidence that a write failed. Other queue entries are never consumed or dropped.
- ACK is available only through the bound context and binds event/client/thread/input. ACK is receipt, not completion. At a later scheduled poll, an ACKed event with an idle thread and still-ready task can use the next activation slot.
- A progress fingerprint contains only the public checkpoint, milestone and evidence references; a new branch SHA alone does not reset it. Two activations at unchanged progress stall that task, including across renamed batches. Changed public progress permits reconsideration subject to the protective activation budget, cooldown and expiry. The local activation cap counts all retained records; changing the remote batch ID cannot recharge it. A future finite registration needs trusted foreground reconciliation within existing authorization; do not remove unknown receipts or automatically reset limits. No automatic budget recharge occurs.

## Candidate files and evidence

`continuation.py` implements the optional pulse and ACK helper. `poll.py` is a staged copy with a call under its existing lock and two additional GET allowlists (V4 branch refs and the fixed Work Packages path at a 40-character SHA). Existing reviewed Issue comment publication is unchanged. `session_delivery.py` is a byte-identical copy of the deployed Advisor notification helper; the new continued-work path does not call its active `turn/steer` behavior.

`test_continuation.py` uses fake RPC and synthetic public GitHub content. `test_poll_continuation.py` checks the original lock and restricted read paths. `test_session_delivery.py` preserves the Advisor helper's existing Fake RPC regression tests. All candidate imports run inside the reviewed outer A01 sandbox, with no production credentials/network or checkout write authority. Real CLI/daemon/account identity, live session behavior, launchd restart and actual paced multi-round continuation are not validated by these fixtures.

Raw author records are outside the repository under the isolated `continuation-author` experiment directory. They include commands, explicit environment, before/after source fingerprints, profile fingerprint, exit status and original stdout/stderr. No production deployment is implied by a passing fixture result.

Author sandbox run 04: 41 tests passed, zero skipped, exit 0, before/after candidate fingerprints unchanged. Earlier run 01 (19), run 02 (38) and run 03 (40) remain retained as development snapshots; they are not added to the final count. These are synthetic fixture checks, not live integration acceptance.
