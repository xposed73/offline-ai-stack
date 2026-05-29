@echo off
title Offline AI Stack - One-Click Launcher
cls
cd /d "%~dp0"
echo ==========================================================
echo         OFFLINE AI STACK - ONE-CLICK LAUNCHER
echo ==========================================================
echo.
echo [1/3] Verifying host environment and dependencies...
echo (First-time setup will automatically download 'uv' and python libraries)
echo.

:: Execute PowerShell Bootstrap Script
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\bootstrap.ps1"
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Environment setup failed. Read warnings above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Initializing local database services ^& private AI models...
echo (Images and LLMs will download automatically in the background)
echo.

:: Run start orchestrator
call "%~dp0.venv\Scripts\offline-ai.exe" start
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to start Docker services or model pulls.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Launching your local unified Web Control Panel...
start "" "http://localhost:8000"

echo.
echo ==========================================================
echo       🚀 STACK IS NOW ONLINE AND READY FOR USE! 🚀
echo ==========================================================
echo * Web Control Panel: http://localhost:8000
echo * OpenWebUI Portal:  http://localhost:3000
echo * n8n Web Console:   http://localhost:5678
echo * Qdrant Database:   http://localhost:6333/dashboard
echo ==========================================================
echo To shut down all services, double-click 'stop_stack.bat'.
echo.
echo Launching local FastAPI service...

:: Start background REST service
call "%~dp0.venv\Scripts\offline-ai.exe" serve
pause
