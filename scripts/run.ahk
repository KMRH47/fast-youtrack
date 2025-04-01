#Requires AutoHotkey v2.0

; define and initialize globals first
global UserSettingsDir := A_ScriptDir "\..\user"
global LogDir := A_ScriptDir "\..\logs"

RunApp(baseDir := A_ScriptDir "\..") {
    ; update globals for current context
    UserSettingsDir := baseDir "\user"
    LogDir := baseDir "\logs"

    entryPath := A_IsCompiled ?
        baseDir . "\python_app.exe" :
            Format('"{1}" "{2}"', baseDir . "\venv\Scripts\pythonw.exe", baseDir . "\src\main.py")
    pidFile := baseDir . "\pids\python.pid"
    pidDir := baseDir . "\pids"

    ; activate existing window if PID file exists
    if (FileExist(pidFile) && ActivateExistingWindow(pidFile)) {
        return
    }

    ; get or prompt for the active subdomain
    activeSubdomain := GetActiveSubdomain() || DisplaySubdomainPicker()
    if (!activeSubdomain) {
        return
    }
    ; create passphrase key file
    CreateKey(activeSubdomain.passphrase, activeSubdomain.subdomain)

    ; run script
    Run(A_IsCompiled
        ? Format('"{1}" "{2}" "{3}"', entryPath, activeSubdomain.passphrase, activeSubdomain.subdomain)
            : Format('{1} "{2}" "{3}"', entryPath, activeSubdomain.passphrase, activeSubdomain.subdomain)
        ,
        ,
        ,
        &pid)

    ; ensure pid dir exists
    if (!DirExist(pidDir)) {
        DirCreate(pidDir)
    }

    if FileExist(pidFile)
        FileDelete(pidFile)
    FileAppend(pid, pidFile)

    ; show splash screen until tkinter UI (main window) appears
    SetTimer(ShowStartupSplash.Bind(pid), 100)
}

; include after globals are defined and initialized (ignore errors)
#Include %A_ScriptDir%\ahk\youtrack.ahk
#Include %A_ScriptDir%\ahk\utils.ahk

; CTRL + SHIFT + T
^+t:: {
    rootDir := RegExReplace(A_ScriptDir, "\\scripts$", "")
    RunApp(rootDir)
}
