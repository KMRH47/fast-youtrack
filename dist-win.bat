@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: paths
set "AHK_COMPILER=C:\Program Files\AutoHotkey\Compiler\Ahk2Exe.exe"
set "AHK_BASE=C:\Program Files\AutoHotkey\v2\AutoHotkey.exe"
set "PROJECT_ROOT=%~dp0"
if "%PROJECT_ROOT:~-1%" == "\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "TEMP_DIR=%DIST_DIR%\temp"

echo Creating FastYouTrack distribution...

:: distribution structure
rd /s /q %DIST_DIR% 2>nul
mkdir %DIST_DIR% 2>nul
mkdir %DIST_DIR%\user 2>nul
mkdir %TEMP_DIR% 2>nul

:: create standalone marker
echo 1 > %DIST_DIR%\STANDALONE

:: copy user data with proper path quoting and trailing backslash
echo Copying user data...
if exist "%PROJECT_ROOT%\user\" (
    xcopy "%PROJECT_ROOT%\user\*" "%DIST_DIR%\user\" /E /I /Y /Q >nul
) else (
    echo WARNING: Source user data directory not found: "%PROJECT_ROOT%\user"
)

:: compile Python app
echo Compiling Python application...
(
echo from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata
echo hiddenimports = collect_submodules('dependency_injector')
echo hiddenimports += [
echo 'dependency_injector.errors',
echo 'dependency_injector.wiring',
echo 'dependency_injector.providers',
echo 'dependency_injector.containers',
echo 'dependency_injector._declarations',
echo 'dependency_injector._containers',
echo 'dependency_injector.providers.singleton',
echo 'dependency_injector.providers.factory',
echo 'dependency_injector._utils',
echo 'dependency_injector.cpp_utils',
echo 'dependency_injector.providers_types',
echo ]
echo datas = collect_data_files('dependency_injector')
echo datas += copy_metadata('dependency_injector')
)> "%TEMP_DIR%\hook-dependency_injector.py"

pip show pyinstaller >nul 2>&1 || pip install pyinstaller -q

pyinstaller --onefile --clean --windowed ^
    --paths=%PROJECT_ROOT% ^
    --paths=%PROJECT_ROOT%\src ^
    --additional-hooks-dir=%TEMP_DIR% ^
    --hidden-import=dependency_injector.errors ^
    --hidden-import=dependency_injector.wiring ^
    --hidden-import=dependency_injector._utils ^
    --hidden-import=dependency_injector.providers ^
    --hidden-import=dependency_injector.containers ^
    --hidden-import=dependency_injector.cpp_utils ^
    %PROJECT_ROOT%\src\main.py ^
    --name python_app.exe ^
    --distpath %DIST_DIR% ^
    --workpath %TEMP_DIR%\build ^
    --specpath %TEMP_DIR%

:: compile AHK launcher
echo Compiling AHK launcher...

:: create necessary directories for compilation
mkdir "%TEMP_DIR%\ahk" 2>nul

:: copy AHK files to temp directory
copy "%PROJECT_ROOT%\scripts\ahk\*.ahk" "%TEMP_DIR%\ahk\" /Y >nul
copy "%PROJECT_ROOT%\scripts\run.ahk" "%TEMP_DIR%\" /Y >nul

:: Create the main combined script in temp root
echo Creating combined AHK script...
(
echo #Requires AutoHotkey v2.0
echo #SingleInstance Force
echo #Warn All, Off
echo.
echo ; Define and Initialize globals for compiled context
echo global UserSettingsDir := A_ScriptDir "\user"
echo global LogDir := A_ScriptDir "\logs"
echo.
echo ; Include all components from the 'ahk' subfolder relative to this script
echo #Include ahk\utils.ahk
echo #Include ahk\gui-utils.ahk
echo #Include ahk\gui.ahk
echo #Include ahk\youtrack.ahk
echo #Include run.ahk
echo.
echo ; Register OnExit
echo OnExit DeleteKeys
echo.
echo ; Call the main function
echo RunApp^(A_ScriptDir^)
)>"%TEMP_DIR%\combined.ahk"

:: verify file was created
if not exist "%TEMP_DIR%\combined.ahk" (
    echo ERROR: Failed to create combined.ahk! Check permissions and paths.
    pause
    exit /b 1
)

:: compile to EXE
echo Starting AHK compilation...
"%AHK_COMPILER%" /in "%TEMP_DIR%\combined.ahk" /out "%DIST_DIR%\FastYouTrack.exe" /base "%AHK_BASE%"

:: verify compilation success based on errorlevel and file existence
if errorlevel 1 (
    echo ERROR: Ahk2Exe.exe reported an error (Code: %errorlevel%)!
    pause
    exit /b 1
)
if not exist "%DIST_DIR%\FastYouTrack.exe" (
    echo ERROR: Ahk2Exe.exe finished but FastYouTrack.exe was not created!
    pause
    exit /b 1
)

echo Compilation successful.

:: clean up temporary files
echo Cleaning up...
rd /s /q "%TEMP_DIR%" 2>nul

echo Distribution successfully created in %DIST_DIR%
echo.
ENDLOCAL