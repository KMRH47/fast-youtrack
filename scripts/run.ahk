#Requires AutoHotkey v2.0
#Include ahk/youtrack.ahk

; CTRL SHIFT T
^+t:: {
    activeSubdomain := GetActiveSubdomain() || DisplaySubdomainPicker()
    if (!activeSubdomain) {
        return
    }

    CreateKey(activeSubdomain.passphrase, activeSubdomain.subdomain)
    Run(A_WorkingDir '\..\venv\Scripts\pythonw.exe ../src/main.py "' activeSubdomain.passphrase '" "' activeSubdomain.subdomain '"')
}
