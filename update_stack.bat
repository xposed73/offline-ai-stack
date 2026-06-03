@echo off
title Offline AI Stack - Update Tool
cls
cd /d "%~dp0"
echo ==========================================================
echo              OFFLINE AI STACK - UPDATE TOOL
echo ==========================================================
echo.
echo Pulling latest updates from Git...
echo.

:: Run git pull
git pull
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to pull updates from Git. Please check your internet connection or git status.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==========================================================
echo             CODEBASE UPDATED SUCCESSFULLY!
echo ==========================================================
echo Your local offline AI stack has been updated to the latest version.
echo.
pause
