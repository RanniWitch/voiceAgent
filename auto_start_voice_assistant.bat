@echo off
REM Auto-start Voice Assistant on Windows Boot
echo Starting Voice Assistant...

REM Change to the voice assistant directory
cd /d "C:\Users\SaiPC\voiceAgent\voiceAgent"

REM Activate virtual environment and start assistant
call venv\Scripts\activate.bat

REM Start the voice assistant (auto-start version)
py wake_word_assistant_auto.py

REM Keep window open if there's an error
if errorlevel 1 pause
