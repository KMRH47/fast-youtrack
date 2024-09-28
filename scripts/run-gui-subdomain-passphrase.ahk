#Requires AutoHotkey v2.0
#Include run-gui.ahk
#include run-lib.ahk

/** @param {Array} listBoxItems */
ShowSubdomainsPassphraseWindow() {

    subdomainTitle := "Select a subdomain:"
    subdomains := GetSubdomains(baseDir)

    passphraseTitle := "Enter passphrase:"
    passphraseAndSubdomain := PromptPassphraseAndSubdomain(passphraseTitle, subdomainTitle, subdomains)

    return passphraseAndSubdomain
}

/** @param {Array} listBoxItems */
PromptPassphraseAndSubdomain(passphraseTitle, listBoxTitle, listBoxItems) {
    customWindow := CreatePassAndListWindow(passphraseTitle, listBoxTitle, listBoxItems)
    customWindow.OnEvent("Escape", (*) => customWindow.Destroy())
    DisplayOnTop(customWindow)

    return PassphraseResult(customWindow.SelectedValues.item, customWindow.SelectedValues.passphrase)
}

class PassphraseResult {
    subdomain := ""
    passphrase := ""

    __New(subdomain, passphrase) {
        this.subdomain := subdomain
        this.passphrase := passphrase
    }

    ToString() {
        return "subdomain: " this.subdomain "`npassphrase: " this.passphrase
    }
}
