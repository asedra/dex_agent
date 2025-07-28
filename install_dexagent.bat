@echo off
title DexAgent Windows Installer
echo =============================================
echo DexAgent - Windows PowerShell Agent Installer
echo =============================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo ✓ Python is installed
echo.

REM Check Python version
echo [2/4] Checking Python version...
python -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    python -c "import sys; print(f'Current version: {sys.version}')"
    echo.
    pause
    exit /b 1
)

echo ✓ Python version is compatible
echo.

REM Install required packages
echo [3/4] Installing required Python packages...
echo Installing websockets, psutil, requests...
pip install websockets psutil requests

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required packages
    echo Please make sure you have internet connection and try again
    echo.
    echo You can also try installing manually:
    echo   pip install websockets
    echo   pip install psutil  
    echo   pip install requests
    echo.
    pause
    exit /b 1
)

echo ✓ All packages installed successfully
echo.

REM Create desktop shortcut (optional)
echo [4/4] Creating desktop shortcut...
set "current_dir=%cd%"
set "shortcut_target=%current_dir%\dexagent_windows.py"
set "desktop=%USERPROFILE%\Desktop"

echo @echo off > "%desktop%\DexAgent.bat"
echo title DexAgent - Windows PowerShell Agent >> "%desktop%\DexAgent.bat"
echo cd /d "%current_dir%" >> "%desktop%\DexAgent.bat"
echo python dexagent_windows.py >> "%desktop%\DexAgent.bat"
echo pause >> "%desktop%\DexAgent.bat"

if exist "%desktop%\DexAgent.bat" (
    echo ✓ Desktop shortcut created at %desktop%\DexAgent.bat
) else (
    echo ⚠ Could not create desktop shortcut
)

echo.
echo =============================================
echo INSTALLATION COMPLETE!
echo =============================================
echo.
echo Next steps:
echo 1. Edit the configuration in dexagent_windows.py
echo    - Change server_url to your DexAgents server
echo    - Change api_token to your API token
echo    - Customize agent_name and tags
echo.
echo 2. Run the agent:
echo    - Double-click DexAgent.bat on your desktop, OR
echo    - Run: python dexagent_windows.py
echo.
echo 3. The agent will show a GUI window where you can:
echo    - Monitor connection status
echo    - View activity logs
echo    - Configure settings
echo    - Test connection
echo.
echo For support, check the DexAgents documentation.
echo.
pause