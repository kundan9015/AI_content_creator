@echo off
REM Windows batch script to start the scheduler

echo Starting AI Content Creator Scheduler...
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the scheduler
python main.py --start-scheduler

pause
