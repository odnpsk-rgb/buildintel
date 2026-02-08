@echo off
chcp 65001 >nul
title Building BuildIntel.exe
cd /d "%~dp0"

echo ========================================
echo   Building BuildIntel.exe
echo ========================================
echo.
echo This will create an .exe file that can be
echo launched with a double-click (no terminal)
echo.
echo IMPORTANT: This may take 5-10 minutes!
echo.
pause

echo.
echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Step 2: Installing/upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 3: Installing dependencies...
pip install PyQt5==5.15.10 requests==2.31.0

echo.
echo Step 4: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 5: Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "BuildIntel.spec" del /q BuildIntel.spec

echo.
echo Step 6: Building .exe file...
echo This may take several minutes, please wait...
echo.

REM Build with all necessary imports and modules
pyinstaller --name=BuildIntel --onefile --windowed --add-data="ui;ui" --hidden-import=PyQt5 --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.sip --hidden-import=api_client --hidden-import=requests --collect-all=PyQt5 --collect-submodules=PyQt5 --clean --noconfirm main.py

echo.
if exist "dist\BuildIntel.exe" (
    echo ========================================
    echo SUCCESS! Build completed!
    echo ========================================
    echo.
    echo Your .exe file is ready:
    echo Location: dist\BuildIntel.exe
    echo.
    echo You can now:
    echo 1. Double-click dist\BuildIntel.exe to run
    echo 2. No terminal window will appear!
    echo.
    echo IMPORTANT: Make sure backend server is running
    echo before launching the .exe file!
    echo.
    echo Backend should be at: http://localhost:8000
    echo.
    explorer dist
) else (
    echo ========================================
    echo ERROR: Build failed!
    echo ========================================
    echo.
    echo Check the error messages above.
    echo.
    echo Common issues:
    echo 1. Dependencies not installed
    echo 2. PyInstaller installation failed
    echo 3. Python version incompatible
    echo.
)

pause
