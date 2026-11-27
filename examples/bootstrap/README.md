# Project bootstrap preview

Use a reviewed installation of the CLI with the pinned protocol dependencies.
Commands below are examples, not execution evidence. Keep the saved plan outside
the target, because any target change invalidates it.

```sh
mkdir /private/tmp/example-project
python3 scripts/v4_project.py plan-init --root /private/tmp/example-project \
  --owner example-owner --project-id example-project > /private/tmp/example-plan.json
# Inspect every proposed file and copy its plan_sha256 exactly.
python3 scripts/v4_project.py apply --root /private/tmp/example-project \
  --plan /private/tmp/example-plan.json --plan-sha256 <exact-plan-sha256>
python3 scripts/v4_local.py inspect --root /private/tmp/example-project
```

On macOS use canonical paths (for example `/private/tmp/...`, not the `/tmp`
symlink) for this controller. Use `plan-import` for an existing directory; native
agent instruction files are retained. This preview installs only neutral rules.
CLAUDE/Codex adapters and a complete new-project-to-provider workflow are pending.

To preview assets from a newer reviewed template, run its `plan-upgrade` CLI.
Apply requires no live/unknown execution and never changes the task authority.
`rollback --operation-id <transaction-id>` uses the returned installation receipt.
It stops on changed files, superseding installations or unresolved writes.

The initial WP is planned with unknown budget and no authorization. Inspect and
review the foundation before explicitly importing runnable task/resource data in
a separate disposable demo. The public protocol example is synthetic, not a
production permission grant. Do not change live JSON to bypass the controller.
