#Requires AutoHotkey v2.0

/** @param {Array} comboBoxItems 
 * @return {Object|false} */
CreatePassAndListWindow(passphraseLabel, comboBoxLabel, comboBoxItems) {
    customGui := Gui("+AlwaysOnTop")
    customGui.SetFont("s10")
    customGui.OnEvent("Close", (*) => customGui.Destroy())
    customGui.OnEvent("Escape", (*) => customGui.Destroy())
    customGui.SelectedValues := {}

    combobox := AddComboBox(customGui, comboBoxLabel, comboBoxItems)
    passphraseInput := AddPassphraseInput(customGui, passphraseLabel)
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

OnTop() {
    ib_ahk := 'ahk_class #32770 ahk_exe AutoHotkey64.exe'
    if WinExist(ib_ahk) {
        WinSetAlwaysOnTop(1, ib_ahk)
    }
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

; Global variable to hold the timer function
global FadeStepTimer := 0

/**
 * Fades the background color in steps, called by SetTimer.
 * @param {Gui.Text} control
 * @param {Object} startRGB
 * @param {Object} stepRGB
 * @param {Integer} steps
 * @param {Integer&} currentStep
 */
FadeStep(control, startRGB, stepRGB, steps, &currentStep) {
    global FadeStepTimer

    controlExists := WinExist(control)

    ; Stop the timer if the control no longer exists
    if (!controlExists) {
        SetTimer(FadeStepTimer, 0)
        return
    }

    ; Suspend redrawing
    SendMessage 0x000B, 0, 0, , control.Hwnd  ; WM_SETREDRAW, wParam = FALSE

    ; Calculate intermediate color
    newR := Round(startRGB.R + stepRGB.R * currentStep)
    newG := Round(startRGB.G + stepRGB.G * currentStep)
    newB := Round(startRGB.B + stepRGB.B * currentStep)
    intermediateColor := RGBToHex(newR, newG, newB)

    ; Set the new background color
    control.Opt("Background" . intermediateColor)

    ; Resume redrawing
    SendMessage 0x000B, 1, 0, , control.Hwnd  ; WM_SETREDRAW, wParam = TRUE

    ; Force a redraw
    control.Redraw()

    ; Increment the step
    currentStep++

    ; Stop the timer when the fade is complete
    if (currentStep > steps) {
        SetTimer(FadeStepTimer, 0)
    }
}

/**
 * Starts a timer to fade the control's background color over time.
 * @param {Gui.Text} control The control whose background color will fade.
 * @param {Object} startRGB The starting RGB values.
 * @param {Object} stepRGB The step changes for RGB values per timer tick.
 * @param {Integer} steps The total number of steps for the fade.
 */
StartFadeTimer(control, startRGB, stepRGB, steps) {
    global FadeStepTimer
    currentStep := 0

    if (FadeStepTimer) {
        SetTimer(FadeStepTimer, 0)
    }
    FadeStepTimer := (*) => FadeStep(control, startRGB, stepRGB, steps, &currentStep)
    SetTimer(FadeStepTimer, 15)
}

/**
 * Fades the background color of a control over time.
 * @param {Gui.Text} control
 * @param {String} startColor The starting color in hex format (e.g., "FF6961").
 * @param {String} endColor The ending color in hex format (e.g., "FFFFFF").
 * @param {Integer} steps The number of steps to take during the fade.
 */
FadeToDefaultColor(control, startColor, endColor, steps) {
    startRGB := HexToRGB(startColor)
    endRGB := HexToRGB(endColor)

    stepRGB := {
        R: (endRGB.R - startRGB.R) / steps,
        G: (endRGB.G - startRGB.G) / steps,
        B: (endRGB.B - startRGB.B) / steps
    }
    StartFadeTimer(control, startRGB, stepRGB, steps)
}

/**
 * Converts a hex color string to an RGB object.
 * @param {String} hexColor The color in hex format (e.g., "FF6961").
 * @return {Object} An object with R, G, B properties.
 */
HexToRGB(hexColor) {
    hexColor := StrReplace(hexColor, "0x")
    return {
        R: Integer("0x" . SubStr(hexColor, 1, 2)),
        G: Integer("0x" . SubStr(hexColor, 3, 2)),
        B: Integer("0x" . SubStr(hexColor, 5, 2))
    }
}

/**
 * Converts RGB values to a hex color string.
 * @param {Integer} r The red component (0-255).
 * @param {Integer} g The green component (0-255).
 * @param {Integer} b The blue component (0-255).
 * @return {String} The color in hex format (e.g., "FF6961").
 */
RGBToHex(r, g, b) {
    return Format("{:02X}{:02X}{:02X}", r, g, b)
}
