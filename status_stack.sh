#!/usr/bin/env bash
# ==============================================================================
# Offline AI Stack - Status Monitor Wrapper
# ==============================================================================
# This script monitors the status of the local AI stack services and checks
# system hardware compliance on macOS/Linux.
# ==============================================================================

set -euo pipefail

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Execute status script
exec ./scripts/status.sh
