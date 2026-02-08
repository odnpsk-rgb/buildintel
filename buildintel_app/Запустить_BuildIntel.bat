@echo off
chcp 65001 >nul
title BuildIntel
cd /d "%~dp0"

echo ========================================
echo    BuildIntel - AI Assistant
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.9+ and add it to PATH
    echo.
    pause
    exit /b 1
)

REM Проверка зависимостей
echo Checking dependencies...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: PyQt5 not found!
    echo ========================================
    echo.
    echo Installing PyQt5...
    pip install PyQt5==5.15.10
    if errorlevel 1 (
        echo.
        echo Installation failed! Please run: УСТАНОВИТЬ_ЗАВИСИМОСТИ.bat
        pause
        exit /b 1
    )
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo requests not found. Installing...
    pip install requests==2.31.0
    if errorlevel 1 (
        echo.
        echo Installation failed! Please run: УСТАНОВИТЬ_ЗАВИСИМОСТИ.bat
        pause
        exit /b 1
    )
)

echo.
echo Starting BuildIntel...
echo.
echo IMPORTANT: Make sure the backend server is running!
echo Backend should be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the application
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Application failed to start
    echo ========================================
    echo.
    echo Possible solutions:
    echo 1. Install dependencies: pip install -r requirements.txt
    echo 2. Make sure backend is running: python -m uvicorn backend.main:app --reload
    echo 3. Check Python version: python --version (should be 3.9+)
    echo.
    pause
)
