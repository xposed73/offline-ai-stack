#!/usr/bin/env bash
# ==============================================================================
# Offline AI Stack - System Status Monitor
# ==============================================================================
# This script monitors the status of the local AI stack services and checks
# system hardware compliance on macOS/Linux.
# ==============================================================================

set -euo pipefail

# ANSI color codes
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
WHITE='\033[1;37m'
RESET='\033[0m'

# Ensure UTF-8 output encoding
export PYTHONUTF8=1

# Write colorful headers
echo -e "${CYAN}==========================================================${RESET}"
echo -e "${GREEN}          OFFLINE AI STACK - STATUS MONITOR               ${RESET}"
echo -e "${CYAN}==========================================================${RESET}"
echo ""

# Check if virtual environment and CLI executable exist
if [ ! -f ".venv/bin/offline-ai" ]; then
    echo -e "${RED}[ERROR] Virtual environment executable not found.${RESET}"
    echo -e "${WHITE}Please run './start_stack.sh' (or scripts/bootstrap.sh) first to setup the environment.${RESET}"
    exit 1
fi

# Run the stack status command
echo -e "${YELLOW}[1/2] Checking stack service status...${RESET}"
echo ""
if ! .venv/bin/offline-ai status; then
    echo -e "${YELLOW}[WARNING] Failed to run stack status command.${RESET}"
fi

echo ""
# Run the system hardware & dependency checks
echo -e "${YELLOW}[2/2] Checking system hardware & software requirements...${RESET}"
echo ""
if ! .venv/bin/offline-ai system-check; then
    echo -e "${YELLOW}[WARNING] Failed to run system-check command.${RESET}"
fi

echo ""
echo -e "${GREEN}==========================================================${RESET}"
echo -e "${GREEN}            STATUS MONITORING COMPLETE                    ${RESET}"
echo -e "${GREEN}==========================================================${RESET}"
