@echo off
chcp 65001 >nul
echo Building BuildIntel as .exe file...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check for PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Starting build...
echo This may take a few minutes...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "BuildIntel.spec" del /q BuildIntel.spec

REM Build with PyQt5 - включаем все необходимые модули
pyinstaller --name=BuildIntel --onefile --windowed --add-data="ui;ui" --hidden-import=PyQt5 --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.sip --hidden-import=api_client --hidden-import=requests --collect-all=PyQt5 --collect-submodules=PyQt5 --clean --noconfirm main.py

echo.
if exist "dist\BuildIntel.exe" (
    echo ========================================
    echo SUCCESS! Build completed!
    echo ========================================
    echo.
    echo Executable file: dist\BuildIntel.exe
    echo.
    echo IMPORTANT: The .exe file requires the backend server to be running!
    echo Backend should be at: http://localhost:8000
    echo.
    echo You can now run BuildIntel.exe without terminal window.
    echo.
) else (
    echo ========================================
    echo ERROR: Build failed!
    echo ========================================
    echo Check the error messages above.
    echo.
    echo Make sure:
    echo 1. All dependencies are installed: pip install -r requirements.txt
    echo 2. PyQt5 is installed: pip install PyQt5==5.15.10
    echo 3. Python version is 3.9+
    echo.
)

pause
