# ==============================================================================
# Offline AI Stack - System Status Monitor
# ==============================================================================
# This script monitors the status of the local AI stack services and checks
# system hardware compliance.
# ==============================================================================

$ErrorActionPreference = "Stop"

# Ensure UTF-8 output encoding
$env:PYTHONUTF8=1

# Write colorful headers
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "          OFFLINE AI STACK - STATUS MONITOR               " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\offline-ai.exe")) {
    Write-Host "[ERROR] Virtual environment not found." -ForegroundColor Red
    Write-Host "Please run 'start_stack.bat' (or scripts/bootstrap.ps1) first to setup the environment." -ForegroundColor White
    Exit 1
}

# Run the stack status command
Write-Host "[1/2] Checking stack service status..." -ForegroundColor Yellow
Write-Host ""
try {
    & .venv\Scripts\offline-ai.exe status
} catch {
    Write-Host "[WARNING] Error running stack status command: $_" -ForegroundColor Yellow
}

Write-Host ""
# Run the system hardware & dependency checks
Write-Host "[2/2] Checking system hardware & software requirements..." -ForegroundColor Yellow
Write-Host ""
try {
    & .venv\Scripts\offline-ai.exe system-check
} catch {
    Write-Host "[WARNING] Error running system-check command: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "            STATUS MONITORING COMPLETE                    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
