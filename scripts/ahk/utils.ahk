#Requires AutoHotkey v2.0

/** @param {String} dir
 *  Get all folder names in the given directory. */
GetFolderNames(dir) {
    folderNames := []

    loop files, dir "\*", "D" {
        folderName := A_LoopFileName
        if (folderName) {
            folderNames.Push(folderName)
        }
    }
    return folderNames
}

/** @param {Error} err
 * @param {String} fileName
 * The name of the file to be appended.
 * If the absolute path is not specified, it is assumed to be in A_WorkingDir.
 * The target directory must already exist.
 * Standard output (stdout): Specify an asterisk (*) in FileName to send Text to standard output (stdout).
 * Specify two asterisks (**) in FileName to send Text to standard error output (stderr).
 * */
LogError(err, fileName) {
    scriptDir := RegExReplace(A_ScriptDir, "\\scripts\\ahk$", "")
    logsDir := A_ScriptDir "\..\logs"
    logFile := logsDir "\error.log"
    
    if !DirExist(logsDir)
        DirCreate(logsDir)
    
    ; Get clean stack trace
    stackInfo := RegExReplace(err.Stack, ".*\) : ", "")
    
    logMessage := Format(
        "{1} - ERROR - Unhandled exception:`n`n{2}`n{3}:{4}`n{5}`n`n{6}: {7}`n`n",
        GetTimeStamp(),
        fileName,
        err.File,
        err.Line,
        stackInfo,
        err.What,
        err.Message)
    FileAppend(logMessage, logFile)
}

GetTimeStamp() {
    ms := Format("{:03d}", A_MSec)
    return FormatTime(A_Now, "yyyy-MM-dd HH:mm:ss") " " ms "ms"
}

/** @param {String} pidFile
 * @return {Boolean} Activates the main window if it exists
 */
ActivateExistingWindow(pidFile) {
    if (!FileExist(pidFile)) {
        return false
    }
    
    ; read PID from file
    pid := FileRead(pidFile)
    if (!pid || !IsInteger(pid)) {
        FileDelete(pidFile)
        return false
    }
    
    ; get window handle
    hwnd := GetMainWindow(pid)
    if (!hwnd) {
        FileDelete(pidFile)
        return false
    }
    
    ; activate the window using the handle
    WinShow("ahk_id " hwnd)
    WinRestore("ahk_id " hwnd)
    WinActivate("ahk_id " hwnd)
    return true
}

/** @param {Number} parentPID
 * @return {Number} First child window handle or 0
 */
GetMainWindow(parentPID) {
    try {
        DetectHiddenWindows(true)
        for process in ComObjGet("winmgmts:").ExecQuery("Select * from Win32_Process Where ParentProcessId=" parentPID) {
            if (process && process.ProcessId) {
                winList := WinGetList("ahk_pid " process.ProcessId)
                
                ; return the first window handle (AHK arrays are 1-based)
                if (winList && winList.Length > 0) {
                    return winList[1]
                }
            }
        }
    } catch Error as e {
        LogError(e, "GetMainWindow")
    }
    return 0
}

/** @param {String} text
 *  Show a custom splash screen with text */
ShowSplash(text) {
    static splash := ""
    
    try {
        if (splash != "" && IsObject(splash)) {
            splash.Destroy()
        }
    }
    
    splash := Gui("-Caption +AlwaysOnTop +ToolWindow")
    splash.BackColor := "2E8B57"
    
    splash.SetFont("s13 bold", "Segoe UI")
    splash.AddText("cE0FFE0 Center w200 h60", text)
    
    splash.Show("NoActivate")
    
    return splash
}

/** @param {Number} pid
 *  @param {String} text
 *  Show splash screen until application's main window appears */
ShowStartupSplash(pid, text := "Starting Fast YouTrack...") {
    static attempts := 0
    static splash := ""
    
    if (attempts == 0) {
        splash := ShowSplash(text)
    }
    
    attempts++
    
    if (GetMainWindow(pid) || attempts > 300) {
        try {
            if (splash != "" && IsObject(splash)) {
                splash.Destroy()
            }
        }
        SetTimer(, 0)
        attempts := 0
        return
    }
}
