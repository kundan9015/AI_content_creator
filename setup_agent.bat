@echo off
echo ============================================================
echo    AI CONTENT CREATOR - LOCAL AGENT SETUP
echo ============================================================
echo.

REM Check if cloud URL is provided
if "%1"=="" (
    echo Error: Cloud URL required!
    echo.
    echo Usage: setup_agent.bat https://your-app.onrender.com
    echo.
    pause
    exit /b 1
)

set CLOUD_URL=%1

echo Cloud URL: %CLOUD_URL%
echo.

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Step 2: Checking dependencies...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install requests
)

echo.
echo Step 3: Registering with cloud...
python local-agent\agent.py --cloud-url %CLOUD_URL% --register
if errorlevel 1 (
    echo ERROR: Registration failed!
    pause
    exit /b 1
)

echo.
echo Step 4: Creating Windows Task...
echo.
echo IMPORTANT: Now you need to create a Windows Task Scheduler task:
echo.
echo 1. Open Task Scheduler
echo 2. Create Basic Task
echo 3. Name: AI Content Agent
echo 4. Trigger: At startup
echo 5. Action: Start a program
echo    Program: python
echo    Arguments: local-agent\agent.py
echo    Start in: %CD%
echo 6. Finish
echo.

echo ============================================================
echo    SETUP COMPLETE!
echo ============================================================
echo.
echo To start agent manually:
echo   python local-agent\agent.py
echo.
echo To stop agent: Press Ctrl+C
echo.
pause
