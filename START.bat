@echo off
echo ============================================================
echo    AI CONTENT CREATOR - WINDOWS STARTER
echo ============================================================
echo.
echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo.
echo Checking dependencies...
pip show moviepy >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Dependencies already installed!
)

echo.
echo Checking configuration...
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file and add:
    echo - FACEBOOK_ACCESS_TOKEN
    echo - FACEBOOK_PAGE_ID
    echo.
    notepad .env
)

echo.
echo Initializing project...
python main.py --init

echo.
echo ============================================================
echo    SETUP COMPLETE!
echo ============================================================
echo.
echo Next steps:
echo 1. Add your video to data/videos/ folder
echo 2. Run: python main.py --add-video data/videos/your_video.mp4
echo 3. Run: python main.py --test-facebook
echo 4. Run: python main.py --upload-now
echo.
echo For help: python main.py --help
echo.
pause
