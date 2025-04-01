#Requires AutoHotkey v2.0

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
