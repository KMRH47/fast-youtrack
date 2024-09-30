#Requires AutoHotkey v2.0
#include utils.ahk
#Include gui.ahk

global UserSettingsDir := A_WorkingDir "\..\user"
global LogDir := A_WorkingDir "\..\logs"

OnExit DeleteKeys

/** @return {ActiveSubdomain|false} */
DisplaySubdomainPicker() {

    subdomainTitle := "Select a subdomain:"
    subdomains := GetFolderNames(UserSettingsDir)

    passphraseTitle := "Enter passphrase:"
    result := CreatePassAndListWindow(passphraseTitle, subdomainTitle, subdomains)

    if (!result.HasProp("item") || !result.HasProp("passphrase")) {
        return false
    }

    return ActiveSubdomain(result.item, result.passphrase)
}

/**
 * Retrieves the currently active subdomain and its corresponding passphrase.
 * @return {ActiveSubdomain|false} */
GetActiveSubdomain() {
    subdomains := GetFolderNames(UserSettingsDir)
    for subdomain in subdomains {
        keyFilePath := UserSettingsDir "\" subdomain "\.key"
        if FileExist(keyFilePath) {
            passphrase := FileRead(keyFilePath)
            return ActiveSubdomain(subdomain, passphrase)
        }
    }

    return false
}

/**
 * @param {String} passphrase
 * @param {String} subdomain
 */
CreateKey(passphrase, subdomain) {
    subdomainPath := UserSettingsDir "\" subdomain
    DirCreate(subdomainPath)

    keyFilePath := subdomainPath "\.key"
    keyFile := FileOpen(keyFilePath, "w")
    if (keyFile) {
        keyFile.Write(passphrase)
        keyFile.Close()
    } else {
        MsgBox("Unable to open file for writing.")
    }
}

/**
 * Deletes all ".key" files in subdomain directories upon script exit.
 * @param {String} ExitReason
 * @param {Number} ExitCode
 */
DeleteKeys(ExitReason, ExitCode) {
    subdomains := GetFolderNames(UserSettingsDir)
    for subdomain in subdomains {
        keyFilePath := UserSettingsDir "\" subdomain "\.key"
        if FileExist(keyFilePath) {
            try {
                FileDelete(keyFilePath)
            } catch as err {
                LogError(err, LogDir "\log.txt")
            }
        }
    }
}

class ActiveSubdomain {
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
