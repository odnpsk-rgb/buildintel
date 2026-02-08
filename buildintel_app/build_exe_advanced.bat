@echo off
chcp 65001 >nul
title Building BuildIntel.exe (Advanced)
cd /d "%~dp0"

echo ========================================
echo   Building BuildIntel.exe (Advanced)
echo ========================================
echo.
echo This script will create a proper .exe file
echo with all dependencies included.
echo.
echo IMPORTANT: This may take 10-15 minutes!
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
if exist "build" (
    echo Removing build folder...
    rmdir /s /q build
)
if exist "dist" (
    echo Removing dist folder...
    rmdir /s /q dist
)
if exist "BuildIntel.spec" (
    echo Removing spec file...
    del /q BuildIntel.spec
)

echo.
echo Step 6: Building .exe file with all modules...
echo This will take several minutes, please wait...
echo.

REM Build with comprehensive module collection
pyinstaller ^
    --name=BuildIntel ^
    --onefile ^
    --windowed ^
    --add-data="ui;ui" ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    --hidden-import=PyQt5.sip ^
    --hidden-import=api_client ^
    --hidden-import=requests ^
    --collect-all=PyQt5 ^
    --collect-submodules=PyQt5 ^
    --clean ^
    --noconfirm ^
    main.py

echo.
if exist "dist\BuildIntel.exe" (
    echo ========================================
    echo SUCCESS! Build completed!
    echo ========================================
    echo.
    echo Your .exe file: dist\BuildIntel.exe
    echo File size: 
    dir dist\BuildIntel.exe | find "BuildIntel.exe"
    echo.
    echo You can now double-click BuildIntel.exe
    echo to run the application (no terminal window!)
    echo.
    echo IMPORTANT: Backend server must be running
    echo at http://localhost:8000
    echo.
    explorer dist
) else (
    echo ========================================
    echo ERROR: Build failed!
    echo ========================================
    echo.
    echo Check the error messages above.
    echo.
    echo Try running this script again or check:
    echo 1. All dependencies are installed
    echo 2. PyQt5 is properly installed
    echo 3. Python version is 3.9+
    echo.
    pause
    exit /b 1
)

pause
