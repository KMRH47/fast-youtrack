#Requires AutoHotkey v2.0
#Include run-gui-subdomain-passphrase.ahk

global BaseDir := A_WorkingDir "\..\user-settings"
global KeyFile := BaseDir "\.key"

OnExit DeleteKeyFile

; CTRL SHIFT T
^+t:: {
    global KeyFile

    if FileExist(KeyFile) {
        Run('pythonw "../src/main.py"')
        return
    }

    result := ShowSubdomainsPassphraseWindow()

    if (result and result.HasProp("subdomain") and result.HasProp("passphrase")) {
        Run('pythonw "../src/main.py" "' result.passphrase '" "' result.subdomain '"')
    }
}
