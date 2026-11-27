# Project bootstrap preview

Use a reviewed framework checkout with the pinned Python dependencies and the
required execution isolation. The installer copies neutral rules, a versioned
guide and local authority; it does not copy the CLI or its dependencies into the
target project. Keep that reviewed checkout available to operate the project.

`FRAMEWORK_ROOT` is the checkout containing `scripts/v4_project.py` and
`scripts/v4_local.py`. `TARGET_ROOT` is the project being installed or upgraded.
Use absolute, canonical paths: on macOS `/private/tmp/...`, not the `/tmp` symlink.
The commands below work even when your current directory is `TARGET_ROOT`.
They are usage examples, not execution evidence.

## Empty project or existing project

```sh
FRAMEWORK_ROOT='/absolute/path/to/reviewed-framework'
TARGET_ROOT='/private/tmp/example-project'
PLAN_FILE='/private/tmp/example-plan.json'
RECEIPT_FILE='/private/tmp/example-receipt.json'
mkdir -p "$TARGET_ROOT"
python3 "$FRAMEWORK_ROOT/scripts/v4_project.py" plan-init --root "$TARGET_ROOT" \
  --owner example-owner --project-id example-project > "$PLAN_FILE"
# Review every proposed file. Copy the exact plan_sha256 from PLAN_FILE.
PLAN_SHA='paste-the-reviewed-plan-sha256'
python3 "$FRAMEWORK_ROOT/scripts/v4_project.py" apply --root "$TARGET_ROOT" \
  --plan "$PLAN_FILE" --plan-sha256 "$PLAN_SHA" > "$RECEIPT_FILE"
python3 "$FRAMEWORK_ROOT/scripts/v4_local.py" inspect --root "$TARGET_ROOT"
```

For an existing project, use `plan-import` in place of `plan-init`; do not run both
plans in sequence. Existing code, dirty/untracked work and native agent instruction
files are retained. A conflicting BOOTSTRAP file causes a conflict, not replacement.
Store plans and receipts **outside** the target: changing the target after planning
invalidates the plan. A stale plan must be regenerated and reviewed before apply.
Repeating the same successful apply returns its historical receipt without granting
new work rights.

The initial work package is planned with unknown budget and no authorization. Git
is not initialized implicitly. Inspect and review the foundation before importing
runnable task/resource data through an explicitly reviewed migration. Do not edit
live JSON to bypass the controller. CLAUDE/Codex adapters and a complete
new-project-to-provider workflow are pending.

## Upgrade and roll back that upgrade

Keep the original checkout available. Set `FRAMEWORK_ROOT` to a newer reviewed
checkout while keeping `TARGET_ROOT` unchanged; for example, an installation made
with `0.2.0-preview` can be upgraded by the `0.2.1-preview` controller. The CLI uses
its own checkout's version and guide. Reusing the same version is not evidence of
a cross-version upgrade, and changing guide bytes requires a new version directory.

```sh
FRAMEWORK_ROOT='/absolute/path/to/newer-reviewed-framework'
UPGRADE_PLAN='/private/tmp/example-upgrade-plan.json'
UPGRADE_RECEIPT='/private/tmp/example-upgrade-receipt.json'
python3 "$FRAMEWORK_ROOT/scripts/v4_project.py" plan-upgrade --root "$TARGET_ROOT" \
  > "$UPGRADE_PLAN"
# Review UPGRADE_PLAN and copy its exact plan_sha256.
PLAN_SHA='paste-the-reviewed-upgrade-plan-sha256'
python3 "$FRAMEWORK_ROOT/scripts/v4_project.py" apply --root "$TARGET_ROOT" \
  --plan "$UPGRADE_PLAN" --plan-sha256 "$PLAN_SHA" > "$UPGRADE_RECEIPT"
python3 "$FRAMEWORK_ROOT/scripts/v4_local.py" inspect --root "$TARGET_ROOT"
# To undo this upgrade, copy its transaction_id from UPGRADE_RECEIPT.
TRANSACTION_ID='paste-the-upgrade-transaction-id'
python3 "$FRAMEWORK_ROOT/scripts/v4_project.py" rollback --root "$TARGET_ROOT" \
  --operation-id "$TRANSACTION_ID"
python3 "$FRAMEWORK_ROOT/scripts/v4_local.py" inspect --root "$TARGET_ROOT"
```

Upgrade adds immutable assets and selects the new guide; it does not rewrite the
existing authority or retarget its contract references. Rolling back that upgrade
restores the previous selection and preserves the prior authority. Keep inspecting
both the installation selection and the authority's explicit versioned references.

Apply/rollback refuse live or unknown execution. Rollback stops on edited owned
files, superseding installations, authority references to assets being removed or
unresolved writes. Preserve those results for reconciliation. Rolling back the
initial installation instead removes its unchanged owned assets, including its
initial authority; use the upgrade transaction ID when you intend to undo only an
upgrade. A replayed rollback is historical evidence, not permission to delete a
newer installation.
