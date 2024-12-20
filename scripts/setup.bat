@echo off
setlocal

REM Paths for the virtual environment and AutoHotkey
set VENV_DIR=venv
set VENV_ACTIVATE=%VENV_DIR%\Scripts\activate
set AHK_DIR=ahk
set AHK_URL=https://www.autohotkey.com/download/ahk-v2.zip
set AHK_ZIP=%AHK_DIR%\ahk-v2.zip

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Please install Python manually from https://www.python.org/downloads/
    exit /b 1
)

REM Check if virtual environment exists
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

REM Activate the virtual environment and install dependencies
call %VENV_ACTIVATE%
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Download and set up AutoHotkey portable version
if not exist %AHK_DIR% (
    echo Creating directory for AutoHotkey...
    mkdir %AHK_DIR%

    echo Downloading AutoHotkey v2 portable...
    curl -L %AHK_URL% -o %AHK_ZIP%

    echo Extracting AutoHotkey v2 portable...
    powershell -Command "Expand-Archive -Path %AHK_ZIP% -DestinationPath %AHK_DIR%"

    del %AHK_ZIP%

    REM Check if AutoHotkey64.exe exists
    if not exist %AHK_DIR%\AutoHotkey64.exe (
        echo Failed to download or extract AutoHotkey.
        exit /b 1
    )
    echo AutoHotkey v2 portable setup complete!
) else (
    echo AutoHotkey v2 portable is already set up.
)

echo Setup complete!
