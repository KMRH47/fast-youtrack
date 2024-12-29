@echo off
setlocal

REM Kill previous Fast YouTrack AutoHotkey process if exists, suppress output
set /p PID=<ahk\pid.txt <nul >nul 2>&1
taskkill /F /PID %PID% 2>nul

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

REM Run the AutoHotkey script
start "" /b %AHK_PATH% /restart %AHK_SCRIPT%

REM Capture PID to ahk/pid.txt
powershell -NoProfile -ExecutionPolicy Bypass -Command "$proc = Get-Process AutoHotkey64 | Sort-Object StartTime -Descending | Select-Object -First 1; if ($proc) { $proc.Id } else { exit 1 }" > ahk\pid.txt 2>nul

echo Fast YouTrack running in background...
