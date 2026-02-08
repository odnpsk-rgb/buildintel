@echo off
chcp 65001 >nul
title BuildIntel
cd /d "%~dp0"

echo ========================================
echo    BuildIntel - AI Assistant
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.9+ and add it to PATH
    echo.
    echo Download Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check and install PyQt5
echo [1/3] Checking PyQt5...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyQt5 not found. Installing...
    pip install PyQt5==5.15.10 >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install PyQt5!
        echo.
        echo Try manually: pip install PyQt5==5.15.10
        pause
        exit /b 1
    )
    echo [OK] PyQt5 installed
) else (
    echo [OK] PyQt5 is installed
)

REM Check and install requests
echo [2/3] Checking requests...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [INFO] requests not found. Installing...
    pip install requests==2.31.0 >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install requests!
        echo.
        echo Try manually: pip install requests==2.31.0
        pause
        exit /b 1
    )
    echo [OK] requests installed
) else (
    echo [OK] requests is installed
)

REM Check backend
echo [3/3] Checking backend connection...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend server not responding!
    echo.
    echo IMPORTANT: Backend server must be running!
    echo.
    echo To start backend:
    echo 1. Open terminal in project root
    echo 2. Run: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    echo.
    echo Or use: start.bat from project root
    echo.
    echo Continue anyway? (Y/N)
    choice /C YN /N /M ""
    if errorlevel 2 exit /b 1
) else (
    echo [OK] Backend server is running
)

echo.
echo ========================================
echo Starting BuildIntel...
echo ========================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Application failed to start
    echo ========================================
    echo.
    echo Possible solutions:
    echo 1. Install dependencies: pip install -r requirements.txt
    echo 2. Make sure backend is running
    echo 3. Check Python version: python --version
    echo.
    pause
)
