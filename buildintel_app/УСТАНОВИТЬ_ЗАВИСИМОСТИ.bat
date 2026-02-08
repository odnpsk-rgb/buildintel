@echo off
chcp 65001 >nul
title Installing BuildIntel Dependencies
cd /d "%~dp0"

echo ========================================
echo   Installing BuildIntel Dependencies
echo ========================================
echo.

echo Step 1: Installing PyQt5...
pip install PyQt5==5.15.10

echo.
echo Step 2: Installing requests...
pip install requests==2.31.0

echo.
echo Step 3: Testing installation...
python -c "import PyQt5; import requests; print('SUCCESS: All dependencies installed!')"

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Try manually:
    echo pip install PyQt5==5.15.10 requests==2.31.0
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCCESS! Dependencies installed.
    echo ========================================
    echo.
    echo You can now run: python main.py
    echo Or double-click: Запустить_BuildIntel.bat
    echo.
)

pause
