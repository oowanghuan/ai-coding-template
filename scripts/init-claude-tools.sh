#!/bin/bash
# Preserved V3 CLI entry; the original script is in legacy/v3.3.0/.
set -eu
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/install_claude_tools.py" "$@"
