@echo off
chcp 65001 >nul
title Fix BuildIntel.exe Build
cd /d "%~dp0"

echo ========================================
echo   Fixing BuildIntel.exe Build
echo ========================================
echo.
echo This will rebuild the .exe file with
echo all PyQt5 modules properly included.
echo.

REM Check if PyQt5 is installed
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo Installing PyQt5...
    pip install PyQt5==5.15.10
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo.
echo Building with build.spec file...
echo This ensures all PyQt5 modules are included.
echo.

pyinstaller build.spec --clean --noconfirm

echo.
if exist "dist\BuildIntel.exe" (
    echo ========================================
    echo SUCCESS! Fixed build completed!
    echo ========================================
    echo.
    echo Your fixed .exe file: dist\BuildIntel.exe
    echo.
    echo Try running it now - PyQt5 should be included!
    echo.
    explorer dist
) else (
    echo ERROR: Build failed!
    echo Try using build_exe_advanced.bat instead
)

pause
