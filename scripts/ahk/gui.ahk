#Requires AutoHotkey v2.0
#Include gui-utils.ahk

/** @param {Array} comboBoxItems
 * @return {Object|false} */
CreatePassAndListWindow(passphraseLabel, comboBoxLabel, comboBoxItems) {
    customGui := Gui("+AlwaysOnTop")
    customGui.SetFont("s10")
    customGui.OnEvent("Close", (*) => customGui.Destroy())
    customGui.OnEvent("Escape", (*) => customGui.Destroy())
    customGui.SelectedValues := {}

    AddComboBox(customGui, comboBoxLabel, comboBoxItems)
    AddPassphraseInput(customGui, passphraseLabel)
    AddSubmitButton(customGui)

    DisplayOnTop(customGui)

    return customGui.SelectedValues ? customGui.SelectedValues : false
}

/** @param {Gui} gui
 * @param {Array} comboBoxItems */
AddComboBox(gui, comboBoxLabel, comboBoxItems) {
    gui.AddText("w200", comboBoxLabel)
    comboBox := gui.AddComboBox("r5 w200 vComboBox Choose1", comboBoxItems)
    comboBox.OnEvent("Change", (*) => HandleKeyPress(comboBox, A_EventInfo))
    return comboBox
}

/** @param {Gui} gui */
AddPassphraseInput(gui, label) {
    gui.AddText("w200", label)
    edit := gui.AddEdit("w200 vPassphraseInput Password")
    return edit
}

/** @param {Gui} gui */
AddSubmitButton(gui) {
    ; Default makes the button submit when Enter is pressed
    button := gui.AddButton("Default w200", "Submit")
    button.OnEvent("Click", (*) => SubmitSelection(gui, gui["ComboBox"], gui["PassphraseInput"]))
    return button
}

/** @param {Gui} gui
 * @param {Gui.Control} comboBox
 * @param {Gui.Edit} passphraseInput */
SubmitSelection(gui, comboBox, passphraseInput) {
    if (comboBox.Text == "") {
        HandleError(gui, comboBox)
        return
    }
    if (passphraseInput.Text == "") {
        HandleError(gui, passphraseInput)
        return
    }

    gui.SelectedValues := { item: comboBox.Text, passphrase: passphraseInput.Text
    }
    gui.Destroy()
}

/** @param {Gui} gui */
DisplayOnTop(gui) {
    gui.Show()
    WinWaitClose(gui)
}

/** @param {Gui.Control} control
 * @param {Integer} eventInfo */
HandleKeyPress(control, eventInfo) {
    if (StrLen(control.Text) > 0) {
        control.Opt("Background" . GetDefaultWindowColor())
        control.Redraw()
    }
}

/**
 * @param {Gui} parent
 * @param {Gui.Text} control
 */
HandleError(parent, control) {
    control.Opt("BackgroundFF6961")
    control.Focus()
    FadeToDefaultColor(control, "FF6961", GetDefaultWindowColor(), 30)
}

GetDefaultWindowColor() {
    color := DllCall("GetSysColor", "Int", 5, "UInt")
    return Format("0x{:06X}", color)
}

OnTop() {
    ib_ahk := 'ahk_class #32770 ahk_exe AutoHotkey64.exe'
    if WinExist(ib_ahk) {
        WinSetAlwaysOnTop(1, ib_ahk)
    }
}
