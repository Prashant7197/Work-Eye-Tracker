@echo off
REM Wellness at Work - Eye Tracker Launcher for Windows

echo Starting Wellness at Work - Eye Tracker...

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Setting up...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

REM Launch the application
.venv\Scripts\python.exe main.py

pause
