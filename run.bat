@echo off
title VRCOSC-Bilibili Launcher
color 0b
cd /d "%~dp0"

:: Check and update the local Python environment
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Automatic environment setup failed!
    echo Please check your internet connection and try running run.bat again.
    echo.
    pause
    exit /b 1
)

:: Start the application
echo.
echo ==========================================================
echo Starting VRCOSC-Bilibili (Uvicorn Server)
echo ==========================================================
echo.
runtime\python.exe backend\main.py
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%.
    echo.
    pause
)
