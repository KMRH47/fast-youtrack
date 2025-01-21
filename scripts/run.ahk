#Requires AutoHotkey v2.0
#Include ahk/youtrack.ahk
#Include ahk/utils.ahk

; CTRL + SHIFT + T
^+t:: {
    projectRoot := A_ScriptDir "\..\"
    pidFile := projectRoot "user\pids\python.pid"

    ; Activate existing window if PID file exists
    if (FileExist(pidFile) && ActivateExistingWindow(pidFile)) {
        return
    }

    ; Get or prompt for the active subdomain
    activeSubdomain := GetActiveSubdomain() || DisplaySubdomainPicker()
    if (!activeSubdomain) {
        return
    }

    ; Create passphrase key file
    CreateKey(activeSubdomain.passphrase, activeSubdomain.subdomain)
    
    ; Run the Python script
    Run(Format('"{1}" "{2}" "{3}" "{4}"',
        projectRoot "venv\Scripts\pythonw.exe",
        projectRoot "src\main.py",
        activeSubdomain.passphrase,
        activeSubdomain.subdomain)
        ,
        ,
        ,
        &pid)

    if FileExist(pidFile)
        FileDelete(pidFile)
    FileAppend(pid, pidFile)
}
