@echo off
title Offline AI Stack - Shutdown Tool
cls
cd /d "%~dp0"
echo ==========================================================
echo            OFFLINE AI STACK - SHUTDOWN TOOL
echo ==========================================================
echo.
echo Stopping all running private background containers...
echo.

:: Call stop orchestrator
call "%~dp0.venv\Scripts\offline-ai.exe" stop
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] Failed to shut down some containers. You can close this window.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==========================================================
echo          ALL SERVICES SHUT DOWN SUCCESSFULLY
echo ==========================================================
echo All data remains saved locally inside the ./data directory.
echo.
pause
