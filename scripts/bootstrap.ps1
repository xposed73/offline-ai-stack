# ==============================================================================
# Offline AI Stack - Automated Windows Bootstrap Script
# ==============================================================================
# This script completely automates the installation, virtualenv creation,
# dependency resolution (via Astral uv), and local environment configuration.
# ==============================================================================

$ErrorActionPreference = "Stop"

# Write colorful headers
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "          OFFLINE AI STACK - WINDOWS BOOTSTRAP            " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check for Python
Write-Host "[1/5] Verifying Python Installation..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "  -> Found Python: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "  [Error] Python is not installed or not added to your system environment PATH." -ForegroundColor Red
    Write-Host "  Please install Python 3.11 or 3.12 from python.org and try again." -ForegroundColor White
    Exit 1
}

# 2. Check and Install UV from Astral
Write-Host "[2/5] Verifying Astral 'uv' Package Manager..." -ForegroundColor Yellow
$uvPath = Get-Command uv -ErrorAction SilentlyContinue

if ($null -eq $uvPath) {
    Write-Host "  -> 'uv' was not found in system PATH. Attempting automated installation..." -ForegroundColor Blue
    try {
        powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
        # Refresh Path environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
        Write-Host "  -> 'uv' successfully installed!" -ForegroundColor Green
    } catch {
        Write-Host "  [Error] Automated installation of 'uv' failed: $_" -ForegroundColor Red
        Write-Host "  Please install 'uv' manually from https://github.com/astral-sh/uv and run this script again." -ForegroundColor White
        Exit 1
    }
} else {
    Write-Host "  -> Found 'uv': $uvPath" -ForegroundColor Gray
}

# 3. Create Python Virtual Environment
Write-Host "[3/5] Creating Python Virtual Environment (.venv)..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    & uv venv --python 3.11
    Write-Host "  -> Virtual environment created successfully." -ForegroundColor Green
} else {
    Write-Host "  -> Virtual environment already exists. Skipping creation." -ForegroundColor Gray
}

# 4. Install Dependencies
Write-Host "[4/5] Resolving and Installing Dependencies..." -ForegroundColor Yellow
try {
    # Activate virtual environment temporarily for dependency mapping
    $env:VIRTUAL_ENV = "$(Get-Location)\.venv"
    $env:PATH = "$(Get-Location)\.venv\Scripts;" + $env:PATH
    
    # Run uv sync or uv pip install
    & uv pip install -e .
    Write-Host "  -> Project packages installed successfully in editable development mode." -ForegroundColor Green
} catch {
    Write-Host "  [Error] Failed to install dependencies: $_" -ForegroundColor Red
    Exit 1
}

# 5. Bootstrap local Environment File
Write-Host "[5/5] Checking Configuration Environment Settings..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  -> Created default configuration '.env' from '.env.example'." -ForegroundColor Green
} else {
    Write-Host "  -> Pre-existing configuration '.env' detected. Keeping unchanged." -ForegroundColor Gray
}

# Success Overview
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "        OFFLINE AI STACK PROVISIONED SUCCESSFULLY!         " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To execute local CLI workflows, run the following command:" -ForegroundColor White
Write-Host "  .venv\Scripts\offline-ai system-check" -ForegroundColor Cyan
Write-Host ""
Write-Host "To launch Docker containers and pull local LLMs:" -ForegroundColor White
Write-Host "  .venv\Scripts\offline-ai start" -ForegroundColor Cyan
Write-Host ""
Write-Host "To launch the background REST FastAPI web server:" -ForegroundColor White
Write-Host "  .venv\Scripts\offline-ai serve" -ForegroundColor Cyan
Write-Host ""
Write-Host "Enjoy your fully private local AI stack! 🚀" -ForegroundColor Green
