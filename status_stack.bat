@echo off
title Offline AI Stack - Status Monitor
cls
echo ==========================================================
echo            OFFLINE AI STACK - STATUS MONITOR
echo ==========================================================
echo.
echo Querying local environment and container stack status...
echo.

:: Ensure Python forces UTF-8 output encoding for console symbols
set PYTHONUTF8=1

:: Check if virtual environment exists
if not exist "%~dp0.venv\Scripts\offline-ai.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run 'start_stack.bat' first to bootstrap the environment and download dependencies.
    echo.
    pause
    exit /b 1
)

:: Run the stack status command
call "%~dp0.venv\Scripts\offline-ai.exe" status
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] Failed to retrieve full container and database status.
)

echo.
:: Run hardware and dependency checks
call "%~dp0.venv\Scripts\offline-ai.exe" system-check
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] Failed to complete system check verification.
)

echo.
echo ==========================================================
echo               STATUS MONITORING COMPLETE
echo ==========================================================
echo.
pause
