@echo off
REM Bootstrap the Python environment and install/update required dependencies.
cd /d "%~dp0"
if exist "py.exe" (
    set "PYEXEC=py -3"
) else (
    set "PYEXEC=python"
)
%PYEXEC% -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo Failed to upgrade pip tools.
    exit /b 1
)
%PYEXEC% -m pip install --upgrade -e .
if errorlevel 1 (
    echo Failed to install or update project dependencies.
    exit /b 1
)
echo Dependencies are installed and up to date.
