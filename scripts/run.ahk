#Requires AutoHotkey v2.0
#Include ahk/run-gui-subdomain-passphrase.ahk
#Include ahk/run-gui.ahk

; CTRL SHIFT T
^+t:: {
    activeSubdomain := GetActiveSubdomain() || DisplaySubdomainPicker()
    if (!activeSubdomain) {
        return
    }

    CreateKey(activeSubdomain.passphrase, activeSubdomain.subdomain)
    Run('pythonw "../src/main.py" "' activeSubdomain.passphrase '" "' activeSubdomain.subdomain '"')
}
