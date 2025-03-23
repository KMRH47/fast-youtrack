@echo off
setlocal

set PID_DIR=pids
if not exist %PID_DIR% mkdir %PID_DIR%

REM Kill previous Fast YouTrack AutoHotkey process if exists, suppress output
set /p PID=<%PID_DIR%\ahk.txt <nul >nul 2>&1
taskkill /F /PID %PID% 2>nul

REM Run setup.bat to ensure venv and dependencies are installed
call scripts\setup.bat
if %ERRORLEVEL% neq 0 (
    echo Setup failed. Exiting...
    exit /b 1
)

REM Paths for AutoHotkey
set VENV_DIR=venv
set AHK_PATH=ahk\AutoHotkey64.exe
set AHK_SCRIPT=scripts\run.ahk

REM Run the AutoHotkey script
start "" /b %AHK_PATH% /restart %AHK_SCRIPT%

REM Capture PID to pids/ahk.txt
powershell -NoProfile -ExecutionPolicy Bypass -Command "$proc = Get-Process AutoHotkey64 | Sort-Object StartTime -Descending | Select-Object -First 1; if ($proc) { $proc.Id } else { exit 1 }" > %PID_DIR%\ahk.txt 2>nul
