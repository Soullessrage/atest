@echo off
REM Run the DND World Simulation Studio desktop app.
REM This will first bootstrap and update required Python dependencies.

cd /d "%~dp0"
call bootstrap_env.bat
if errorlevel 1 (
    echo Aborting launch due to dependency install failure.
    exit /b 1
)
if exist "py.exe" (
    py -3 app\ui\main.py
) else (
    python app\ui\main.py
)
