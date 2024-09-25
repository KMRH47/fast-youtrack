@echo off
setlocal

REM Kill all AutoHotkey processes
taskkill /F /IM AutoHotkey64.exe 2>nul

REM Run setup.bat to ensure venv and dependencies are installed
call scripts\setup.bat
if %ERRORLEVEL% neq 0 (
    echo Setup failed. Exiting...
    exit /b 1
)

REM Paths for AutoHotkey and the virtual environment
set VENV_DIR=venv
set VENV_ACTIVATE=%VENV_DIR%\Scripts\activate
set AHK_PATH=ahk\AutoHotkey64.exe
set AHK_SCRIPT=scripts\run.ahk

REM Activate the virtual environment
if exist %VENV_ACTIVATE% (
    echo Activating virtual environment...
    call %VENV_ACTIVATE%
) else (
    echo Virtual environment not found.
    exit /b 1
)

REM Run the AutoHotkey script
echo Running AutoHotkey script...
start "" /b %AHK_PATH% %AHK_SCRIPT%

REM You can change the hotkey in scripts/run.ahk
echo Fast YouTrack running in background...