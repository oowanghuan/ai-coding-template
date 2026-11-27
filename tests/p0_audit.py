#!/usr/bin/env python3
"""Reproduce V3 findings in disposable fixtures; not a V4 implementation or gate.

Usage: python3 tests/p0_audit.py --output /tmp/v3-audit
Exit 0 means the observations match this frozen baseline, NOT that V3 is healthy.
No network, provider calls, installs, or changes to tracked baseline files.
"""
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "8ed245f5a5c7adeebd31b3f31272164ee85a1d39"
SCOPES = ["README.md", "CLAUDE_INIT.md", "CHANGELOG.md", "AUDIT_REPORT.md",
          "AUDIT_RESPONSE.md", "CC_COLLABORATION/_project_context",
          "CC_COLLABORATION/01_workflow", "CC_COLLABORATION/03_templates",
          "CC_COLLABORATION/05_tools", "CC_COLLABORATION/07_phase_gate",
          "CC_COLLABORATION/08_legacy_integration", ".claude", "scripts"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    # Never overwrite a previous run.
    out.mkdir(parents=True, exist_ok=False)
    records = []
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASELINE], cwd=ROOT, text=True).splitlines()
    manifest = []
    for name in tracked:
        if any(name == s or name.startswith(s + "/") for s in SCOPES):
            data = (ROOT / name).read_bytes()
            original = subprocess.check_output(["git", "show", BASELINE + ":" + name], cwd=ROOT)
            if data != original:
                raise RuntimeError("Baseline changed: " + name)
            manifest.append({"path": name, "sha256": digest(data), "bytes": len(data),
                             "lines": len(data.splitlines())})
    (out / "source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    with tempfile.TemporaryDirectory(prefix="v3-p0-") as tmp:
        sandbox = Path(tmp)

        def sanitize(value):
            return value.replace(str(sandbox), "<fixture>").replace(str(ROOT), "<repository>")

        def run(case, argv, cwd, expected_exit, stdin="", env=None):
            result = subprocess.run(argv, cwd=cwd, text=True, input=stdin,
                                    capture_output=True, timeout=20, env=env)
            output = sanitize(result.stdout + result.stderr)
            log_name = case + ".txt"
            (out / log_name).write_text(output)
            row = {"id": case, "command": [sanitize(str(x)) for x in argv],
                   "cwd": sanitize(str(cwd)), "exit_code": result.returncode,
                   "expected_exit": expected_exit, "observation_matches": result.returncode == expected_exit,
                   "log": log_name, "log_sha256": digest(output.encode())}
            records.append(row)
            return row

        original = sandbox / "original"
        original.mkdir()
        shutil.copytree(ROOT / "scripts", original / "scripts")
        shutil.copytree(ROOT / "CC_COLLABORATION/05_tools", original / "CC_COLLABORATION/05_tools")
        (original / ".git").mkdir()  # Only a project marker; no real Git operations in installer.
        run("R01-pristine-install", ["bash", "scripts/init-claude-tools.sh", "--target=."], original, 1)
        run("R02-list-missing-source", ["bash", "scripts/init-claude-tools.sh", "--list"], original, 0)
        run("R03-dry-run-unsupported", ["bash", "scripts/init-claude-tools.sh", "--target=.", "--dry-run"], original, 1)
        run("R04-shell-syntax", ["bash", "-n", "scripts/init-claude-tools.sh"], original, 0)

        # Diagnostic variant changes ONLY the obsolete source path in a temp copy.
        patched = sandbox / "path-only"
        shutil.copytree(original, patched)
        script = patched / "scripts/init-claude-tools.sh"
        script.write_text(script.read_text().replace("_templates/CC_COLLABORATION/05_TOOLS", "CC_COLLABORATION/05_tools"))
        row = run("R05-path-only-install", ["bash", "scripts/init-claude-tools.sh", "--target=."], patched, 0)
        row["files_after"] = sorted(str(p.relative_to(patched)) for p in (patched / ".claude").rglob("*.md"))
        row["observation_matches"] &= len(row["files_after"]) == 37
        row = run("R06-path-only-repeat", ["bash", "scripts/init-claude-tools.sh", "--target=."], patched, 0)
        row["files_after"] = sorted(str(p.relative_to(patched)) for p in (patched / ".claude").rglob("*.md"))
        row["observation_matches"] &= len(row["files_after"]) == 37

        # Further diagnostic variant fixes both postfix counters; never edits source.
        script.write_text(script.read_text().replace("((count++))", "((++count))").replace("((skipped++))", "((++skipped))"))
        row = run("R07-two-fixes-install", ["bash", "scripts/init-claude-tools.sh", "--target=."], patched, 0)
        row["files_after"] = sorted(str(p.relative_to(patched)) for p in (patched / ".claude").rglob("*.md"))
        row["settings_installed"] = (patched / ".claude/settings.json").exists()
        row["observation_matches"] &= len(row["files_after"]) == 37 and not row["settings_installed"]
        custom = patched / ".claude/commands/ai-pm.md"
        custom.write_text("CUSTOM CONTENT\n")
        row = run("R08-existing-file-repeat", ["bash", "scripts/init-claude-tools.sh", "--target=."], patched, 0)
        row["custom_content_preserved"] = custom.read_text() == "CUSTOM CONTENT\n"
        row["observation_matches"] &= row["custom_content_preserved"]

        # Execute the public Ready Set function verbatim from its fenced example.
        command = (ROOT / "CC_COLLABORATION/05_tools/slash-commands/project-pm.md").read_text()
        block = next(b for b in re.findall(r"```python\n(.*?)```", command, re.S) if "def compute_ready_set" in b)
        example = sandbox / "ready-example.py"
        fixture = {"demo": {"status": "pending", "blocked_by": [], "priority": 1, "authorization": "denied"}}
        (sandbox / "docs/demo").mkdir(parents=True)
        example.write_text("import os\n" + block + "\nprint(compute_ready_set(" + repr(fixture) + "))\n")
        row = run("R09-ready-example", [sys.executable, str(example)], sandbox, 1)
        row["scope"] = "Documentation algorithm only; not execution of /project-pm by a provider"
        row["observation_matches"] &= "AttributeError" in (out / row["log"]).read_text()
        # Supply the example's implicit object and filesystem helpers explicitly.
        # This tests its dependency policy, not the existence of a real scheduler.
        helpers = "import os\nclass Record(dict):\n    __getattr__ = dict.__getitem__\ndirectory_exists = os.path.isdir\n"
        example.write_text(helpers + block + "\nprint(compute_ready_set({'demo': Record(" + repr(fixture['demo']) + ")}))\n")
        row = run("R12-ready-with-helpers", [sys.executable, str(example)], sandbox, 0)
        row["scope"] = "Algorithm fixture with explicit Record and directory_exists helpers; authorization denied"
        row["observation_matches"] &= (out / row["log"]).read_text().strip() == "['demo']"

        # Exercise GUI hook receipt handling only; never dispatch the injected text.
        hook_project = sandbox / "hook-project"
        sessions = hook_project / ".claude/gui-sessions"
        sessions.mkdir(parents=True)
        (sessions / "session-demo.cmd").write_text(json.dumps({"cmdId": "audit-1", "command": "/check-progress demo"}))
        hook_env = {"PATH": os.environ.get("PATH", ""), "CLAUDE_PROJECT_DIR": str(hook_project)}
        hook = ROOT / ".claude/hooks/check-gui-cmd.py"
        row = run("R10-hook-receipt", [sys.executable, str(hook)], hook_project, 0, "{}", hook_env)
        row["ack"] = json.loads((sessions / "session-demo.ack").read_text())
        row["observation_matches"] &= row["ack"]["status"] == "received"
        row = run("R11-hook-repeat", [sys.executable, str(hook)], hook_project, 0, "{}", hook_env)
        row["observation_matches"] &= (out / row["log"]).read_text() == ""

    drift = {}
    for installed, source in [("commands", "slash-commands"), ("skills", "skills"), ("subagents", "subagents")]:
        a = {p.name: p for p in (ROOT / "CC_COLLABORATION/05_tools" / source).glob("*.md") if p.name != "README.md"}
        b = {p.name: p for p in (ROOT / ".claude" / installed).glob("*.md") if p.name != "README.md"}
        drift[installed] = {"source_count": len(a), "installed_count": len(b),
                            "source_only": sorted(a.keys() - b.keys()), "installed_only": sorted(b.keys() - a.keys()),
                            "different": sorted(n for n in a.keys() & b.keys() if a[n].read_bytes() != b[n].read_bytes())}
    backup = [p for p in tracked if p.startswith("_backup/")]
    gate = (ROOT / "CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml").read_text()
    result = {"tested_baseline": BASELINE, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "platform": platform.system() + " " + platform.release() + " " + platform.machine(),
              "python": platform.python_version(), "bash": subprocess.check_output(["bash", "--version"], text=True).splitlines()[0],
              "harness_sha256": digest(Path(__file__).read_bytes()), "cases": records, "drift": drift,
              "tracked_backup_files": len(backup), "tracked_backup_bytes": sum((ROOT / p).stat().st_size for p in backup),
              "active_exec_test_e2e_gate_types": re.findall(r"^\s+type: (exec_check|test_check|e2e_check)$", gate, re.M),
              "all_observations_match": all(r["observation_matches"] for r in records),
              "limitations": ["Not an independent review", "No live coding-agent workflow invoked", "No V4 acceptance executed", "No private source data"]}
    (out / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cases": len(records), "all_observations_match": result["all_observations_match"], "output": str(out)}))
    return 0 if result["all_observations_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
