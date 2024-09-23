global KeyFile := A_WorkingDir "\..\data\.key"
OnExit DeleteKeyFile

; CTRL SHIFT T
^+t:: {
    global KeyFile

    if FileExist(KeyFile) {
        Run('pythonw "../src/main.py"')
        return
    }

    passphrase := InputBoxOnTop()

    if (Type(passphrase) = "String" && passphrase != "") {
        Run('pythonw "../src/main.py" "' passphrase '"')
    }
}

InputBoxOnTop() {
    SetTimer(OnTop, 50)
    passphrase := InputBox("Enter Passphrase", "Please enter your passphrase for this session.").value
    SetTimer(OnTop, 0)

    return passphrase

    OnTop() {
        ib_ahk := 'ahk_class #32770 ahk_exe AutoHotkey64.exe'
        if WinExist(ib_ahk) {
            WinSetAlwaysOnTop(1, ib_ahk)
        }
    }
}

DeleteKeyFile(ExitReason, ExitCode) {
    if FileExist(KeyFile) {
        FileDelete(KeyFile)
    }
}