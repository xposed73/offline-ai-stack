#!/usr/bin/env bash
# ==============================================================================
# Offline AI Stack - One-Click Launcher
# ==============================================================================
# This script initializes the environment, starts all containerized database and
# web UI services, registers Ollama models, and runs the FastAPI server.
# ==============================================================================

set -euo pipefail

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "        OFFLINE AI STACK - ONE-CLICK LAUNCHER"
echo "=========================================================="
echo ""
echo "[1/3] Verifying host environment and dependencies..."
echo "(First-time setup will automatically download 'uv' and python libraries)"
echo ""

# Execute Bash Bootstrap Script
if ! ./scripts/bootstrap.sh; then
    echo ""
    echo "[ERROR] Environment setup failed. Read warnings above."
    exit 1
fi

echo ""
echo "[2/3] Initializing local database services & private AI models..."
echo "(Images and LLMs will download automatically in the background)"
echo ""

# Run start orchestrator
if ! .venv/bin/offline-ai start; then
    echo ""
    echo "[ERROR] Failed to start Docker services or model pulls."
    exit 1
fi

echo ""
echo "[3/3] Launching your local unified Web Control Panel..."
if command -v open &>/dev/null; then
    open "http://localhost:8000"
elif command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:8000"
else
    echo "Please visit http://localhost:8000 in your browser."
fi

echo ""
echo "=========================================================="
echo "      🚀 STACK IS NOW ONLINE AND READY FOR USE! 🚀"
echo "=========================================================="
echo "* Web Control Panel: http://localhost:8000"
echo "* OpenWebUI Portal:  http://localhost:3000"
echo "* n8n Web Console:   http://localhost:5678"
echo "* Qdrant Database:   http://localhost:6333/dashboard"
echo "=========================================================="
echo "To shut down all services, run './stop_stack.sh'."
echo ""
echo "Launching local FastAPI service..."

# Start background REST service (exec replaces the shell process)
exec .venv/bin/offline-ai serve
