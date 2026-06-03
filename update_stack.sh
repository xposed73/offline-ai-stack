#!/usr/bin/env bash
# ==============================================================================
# Offline AI Stack - Update Tool
# ==============================================================================
# This script pulls the latest codebase updates from Git.
# ==============================================================================

set -euo pipefail

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "             OFFLINE AI STACK - UPDATE TOOL"
echo "=========================================================="
echo ""
echo "Pulling latest updates from Git..."
echo ""

# Run git pull
if ! git pull; then
    echo ""
    echo "[ERROR] Failed to pull updates from Git. Please check internet connection or git status."
    exit 1
fi

echo ""
echo "=========================================================="
echo "            CODEBASE UPDATED SUCCESSFULLY!"
echo "=========================================================="
echo "Your local offline AI stack has been updated to the latest version."
echo ""
