#!/usr/bin/env python3
"""
GUI Command Hook for Claude Code

This hook checks for pending GUI commands before each user prompt.
When a .cmd file is found, it injects the command into the conversation context.

Usage: Configure in .claude/settings.json under UserPromptSubmit hook.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Session directory relative to project root
SESSIONS_DIR = ".claude/gui-sessions"

def get_project_dir() -> str:
    """Get project directory from environment or cwd."""
    return os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

def get_sessions_dir() -> Path:
    """Get the GUI sessions directory path."""
    project_dir = get_project_dir()
    return Path(project_dir) / SESSIONS_DIR

def find_pending_command() -> Optional[Dict[str, Any]]:
    """Find the first pending command file (.cmd) that hasn't been acknowledged."""
    sessions_dir = get_sessions_dir()

    if not sessions_dir.exists():
        return None

    # Look for .cmd files
    for cmd_file in sessions_dir.glob("session-*.cmd"):
        session_id = cmd_file.stem.replace("session-", "")
        ack_file = sessions_dir / f"session-{session_id}.ack"

        # Skip if already acknowledged
        if ack_file.exists():
            try:
                ack_data = json.loads(ack_file.read_text())
                cmd_data = json.loads(cmd_file.read_text())
                # Check if ACK is for the same command
                if ack_data.get("cmdId") == cmd_data.get("cmdId"):
                    continue
            except:
                pass

        # Found an unacknowledged command
        try:
            cmd_data = json.loads(cmd_file.read_text())
            cmd_data["_session_id"] = session_id
            cmd_data["_cmd_file"] = str(cmd_file)
            return cmd_data
        except json.JSONDecodeError:
            continue

    return None

def write_ack(session_id: str, cmd_id: str, status: str = "received") -> None:
    """Write acknowledgment file."""
    sessions_dir = get_sessions_dir()
    ack_file = sessions_dir / f"session-{session_id}.ack"

    ack_data = {
        "cmdId": cmd_id,
        "status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    try:
        ack_file.write_text(json.dumps(ack_data, indent=2))
    except Exception as e:
        print(f"Warning: Failed to write ACK file: {e}", file=sys.stderr)

def format_command_context(cmd_data: Dict[str, Any]) -> str:
    """Format command data as context for Claude."""
    command = cmd_data.get("command", "")
    source = cmd_data.get("source", "gui")
    context = cmd_data.get("context", {})

    # Build context message
    lines = [
        "",
        "=" * 60,
        "GUI COMMAND RECEIVED",
        "=" * 60,
        f"Command: {command}",
        f"Source: {source}",
    ]

    if context:
        if context.get("featureId"):
            lines.append(f"Feature: {context['featureId']}")
        if context.get("phaseId"):
            lines.append(f"Phase: {context['phaseId']}")
        if context.get("stepId"):
            lines.append(f"Step: {context['stepId']}")

    lines.extend([
        "=" * 60,
        "",
        f"Please execute the command: {command}",
        "",
    ])

    return "\n".join(lines)

def main():
    """Main entry point for the hook."""
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If no valid JSON, just pass through
        sys.exit(0)

    # Check for pending GUI command
    cmd_data = find_pending_command()

    if cmd_data is None:
        # No pending command, pass through
        sys.exit(0)

    # Found a pending command
    session_id = cmd_data.get("_session_id", "")
    cmd_id = cmd_data.get("cmdId", "")

    # Write ACK
    write_ack(session_id, cmd_id, "received")

    # Format and output context as plain text
    # Claude Code hooks: plain text stdout is added as context
    context = format_command_context(cmd_data)
    print(context)
    sys.exit(0)

if __name__ == "__main__":
    main()
