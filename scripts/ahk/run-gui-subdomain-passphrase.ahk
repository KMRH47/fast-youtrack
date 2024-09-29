#Requires AutoHotkey v2.0
#Include run-gui.ahk
#include run-lib.ahk

/** @return {ActiveSubdomain|false} */
DisplaySubdomainPicker() {

    subdomainTitle := "Select a subdomain:"
    subdomains := GetSubdomains()

    passphraseTitle := "Enter passphrase:"
    result := CreatePassAndListWindow(passphraseTitle, subdomainTitle, subdomains)

    if (!result.HasProp("item") || !result.HasProp("passphrase")) {
        return false
    }

    return ActiveSubdomain(result.item, result.passphrase)
}
