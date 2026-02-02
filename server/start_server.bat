@echo off
REM Start the monitoring server
REM Run this script to start the central server

echo ========================================
echo Starting Monitoring Server
echo ========================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if config.py exists
if not exist config.py (
    echo WARNING: config.py not found
    echo Copying from config.example.py...
    copy config.example.py config.py
    echo.
    echo IMPORTANT: Edit config.py to set your API_TOKEN and STORAGE_ROOT
    echo.
    pause
)

echo Starting server...
echo Press Ctrl+C to stop
echo.

python main.py

pause
