# Local project bootstrap (protocol 0.2)

`.ai-org/state.json` is the only task authority. Installation receipts describe
installed files; they never authorize work or certify acceptance.

The installer does not copy the CLI or its Python dependencies into this project.
Keep a reviewed framework checkout with its required dependencies available.
`FRAMEWORK_ROOT` identifies that checkout; `TARGET_ROOT` identifies this project.
Use absolute, canonical paths (on macOS, `/private/tmp/...`, not the `/tmp` symlink).
For example, this command works even when your current directory is the project:

```sh
FRAMEWORK_ROOT='/absolute/path/to/reviewed-framework'
TARGET_ROOT='/absolute/path/to/your-project'
python3 "$FRAMEWORK_ROOT/scripts/v4_local.py" inspect --root "$TARGET_ROOT"
```

1. Read the current snapshot with the command above, using the reviewed controller
   and its required execution isolation. Do not look for `scripts/` in this project.
2. Confirm project goal, scope, Owner, Git baseline, contracts and test commands.
   A newly installed task is planned. No Worker, review or authorization is invented.
3. Before execution, import an explicitly reviewed snapshot and register resources.
   Live authority must not be replaced by editing JSON. The initial controller does
   not yet expose a general task/authorization editing API; those changes require
   a reviewed migration. Do not treat successful installation as execution readiness.
4. Claims use one host's lock, revision and fencing token. Run only the fixed
   synthetic adapter in an isolated environment. Real provider adapters are pending.
5. On interruption, inspect Git, preserved workspaces, operation receipts and
   unknown outcomes. Do not restart a process whose outcome is unknown or delete
   its workspace. A replayed receipt is historical evidence, not renewed permission.

The project installer does not initialize Git, modify existing agent instructions,
run hooks, fetch dependencies, call a provider or create cloud resources. Establish
a Git baseline explicitly before a code task can be claimed.

Plan/apply/rollback are separate commands. Apply requires the exact plan fingerprint
and unchanged target. Rollback preserves edited files and newer ownership claims.
Unknown installation outcomes block task writes until an explicit reconciliation.
