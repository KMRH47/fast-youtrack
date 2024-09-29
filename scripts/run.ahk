#Requires AutoHotkey v2.0
#Include run-gui-subdomain-passphrase.ahk
#Include run-lib.ahk

; CTRL SHIFT T
^+t:: {
    activeSubdomain := getActiveSubdomain() || DisplaySubdomainPicker()
    if (!activeSubdomain) {
        return
    }

    CreateKey(activeSubdomain.passphrase, activeSubdomain.subdomain)
    Run('pythonw "../src/main.py" "' activeSubdomain.passphrase '" "' activeSubdomain.subdomain '"')
}
