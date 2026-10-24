#!/usr/bin/env bash
# ====================================================================
# KidsPlay AI Studio • 1-Click Antigravity to GitHub Sync Shortcut
# ====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

PYTHON_EXEC="python3"
if [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python3"
fi

exec "$PYTHON_EXEC" "$SCRIPT_DIR/scripts/github_sync.py" "$@"
