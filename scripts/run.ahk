#Requires AutoHotkey v2.0
#Include ahk/youtrack.ahk
#Include ahk/utils.ahk

RunApp()

; CTRL + SHIFT + T
^+t:: {
    RunApp()
}

RunApp() {
    projectRoot := A_ScriptDir "\..\"
    pidFile := projectRoot "pids\python.pid"
    pidDir := projectRoot "pids"

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
    Run(Format('"{1}" "{2}" "{3}" "{4}"',
        projectRoot "venv\Scripts\pythonw.exe",
        projectRoot "src\main.py",
        activeSubdomain.passphrase,
        activeSubdomain.subdomain)
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
}