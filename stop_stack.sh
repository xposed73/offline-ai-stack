#!/usr/bin/env bash
# ==============================================================================
# Offline AI Stack - Shutdown Tool
# ==============================================================================
# This script stops all running private background containers on macOS/Linux.
# ==============================================================================

set -euo pipefail

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "           OFFLINE AI STACK - SHUTDOWN TOOL"
echo "=========================================================="
echo ""
echo "Stopping all running private background containers..."
echo ""

# Check if virtual environment and CLI executable exist
if [ ! -f ".venv/bin/offline-ai" ]; then
    echo "[WARNING] Virtual environment executable not found. Containers might not have been provisioned."
    exit 1
fi

# Call stop orchestrator
if ! .venv/bin/offline-ai stop; then
    echo ""
    echo "[WARNING] Failed to shut down some containers."
    exit 1
fi

echo "Stopping local FastAPI service..."
pkill -f ".venv/bin/offline-ai serve" || true

echo ""
echo "=========================================================="
echo "         ALL SERVICES SHUT DOWN SUCCESSFULLY"
echo "=========================================================="
echo "All data remains saved locally inside the ./data directory."
echo ""
