#!/usr/bin/env bash
# ==============================================================================
# Offline AI Stack - Automated macOS/Linux Bootstrap Script
# ==============================================================================
# This script completely automates the installation, virtualenv creation,
# dependency resolution (via Astral uv), and local environment configuration.
# ==============================================================================

set -euo pipefail

# ANSI color codes
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
RED='\033[1;31m'
GRAY='\033[0;37m'
WHITE='\033[1;37m'
RESET='\033[0m'

# Write colorful headers
echo -e "${CYAN}==========================================================${RESET}"
echo -e "${GREEN}          OFFLINE AI STACK - MAC/LINUX BOOTSTRAP          ${RESET}"
echo -e "${CYAN}==========================================================${RESET}"

# 1. Check for Python
echo -e "${YELLOW}[1/5] Verifying Python Installation...${RESET}"
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo -e "${GRAY}  -> Found Python: ${python_version}${RESET}"
else
    echo -e "${RED}  [Error] Python is not installed or not added to your system environment PATH.${RESET}"
    echo -e "${WHITE}  Please install Python 3.11 or 3.12 and try again.${RESET}"
    exit 1
fi

# 2. Check and Install UV from Astral
echo -e "${YELLOW}[2/5] Verifying Astral 'uv' Package Manager...${RESET}"

# Ensure home directory binaries are in path
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

if ! command -v uv &>/dev/null; then
    echo -e "${BLUE}  -> 'uv' was not found in system PATH. Attempting automated installation...${RESET}"
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        # Refresh path mapping
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        echo -e "${GREEN}  -> 'uv' successfully installed!${RESET}"
    else
        echo -e "${RED}  [Error] Automated installation of 'uv' failed.${RESET}"
        echo -e "${WHITE}  Please install 'uv' manually from https://github.com/astral-sh/uv and run this script again.${RESET}"
        exit 1
    fi
else
    uv_path=$(command -v uv)
    echo -e "${GRAY}  -> Found 'uv': ${uv_path}${RESET}"
fi

# 3. Create Python Virtual Environment
echo -e "${YELLOW}[3/5] Creating Python Virtual Environment (.venv)...${RESET}"
if [ ! -d ".venv" ]; then
    uv venv --python 3.11
    echo -e "${GREEN}  -> Virtual environment created successfully.${RESET}"
else
    echo -e "${GRAY}  -> Virtual environment already exists. Skipping creation.${RESET}"
fi

# 4. Install Dependencies
echo -e "${YELLOW}[4/5] Resolving and Installing Dependencies...${RESET}"
# Activate virtual environment temporarily for installation
export VIRTUAL_ENV="$(pwd)/.venv"
export PATH="$(pwd)/.venv/bin:$PATH"

if uv pip install -e .; then
    echo -e "${GREEN}  -> Project packages installed successfully in editable development mode.${RESET}"
else
    echo -e "${RED}  [Error] Failed to install dependencies.${RESET}"
    exit 1
fi

# 5. Bootstrap local Environment File
echo -e "${YELLOW}[5/5] Checking Configuration Environment Settings...${RESET}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}  -> Created default configuration '.env' from '.env.example'.${RESET}"
else
    echo -e "${GRAY}  -> Pre-existing configuration '.env' detected. Keeping unchanged.${RESET}"
fi

# Success Overview
echo -e "${GREEN}==========================================================${RESET}"
echo -e "${GREEN}        OFFLINE AI STACK PROVISIONED SUCCESSFULLY!         ${RESET}"
echo -e "${GREEN}==========================================================${RESET}"
echo ""
echo -e "${WHITE}To execute local CLI workflows, run the following command:${RESET}"
echo -e "${CYAN}  .venv/bin/offline-ai system-check${RESET}"
echo ""
echo -e "${WHITE}To launch Docker containers and pull local LLMs:${RESET}"
echo -e "${CYAN}  .venv/bin/offline-ai start${RESET}"
echo ""
echo -e "${WHITE}To launch the background REST FastAPI web server:${RESET}"
echo -e "${CYAN}  .venv/bin/offline-ai serve${RESET}"
echo ""
echo -e "${GREEN}Enjoy your fully private local AI stack! 🚀${RESET}"
