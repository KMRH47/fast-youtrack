#Requires AutoHotkey v2.0

global UserSettingsDir := A_WorkingDir "\..\user"
global LogDir := A_WorkingDir "\..\logs"

OnExit DeleteKeys

/** @param {String} baseDir
 *  Get subdomains based on folder names within baseDir */
GetSubdomains() {
    subdomains := []

    loop files, UserSettingsDir "\*", "D" {
        subdomain := A_LoopFileName
        if (subdomain) {
            subdomains.Push(subdomain)
        }
    }
    return subdomains
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
 * Retrieves the currently active subdomain and its corresponding passphrase.
 * @return {ActiveSubdomain|false} */
getActiveSubdomain() {
    subdomains := GetSubdomains()
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
 * Deletes all ".key" files in subdomain directories upon script exit.
 * @param {String} ExitReason
 * @param {Number} ExitCode
 */
DeleteKeys(ExitReason, ExitCode) {
    subdomains := GetSubdomains()
    for subdomain in subdomains {
        keyFilePath := UserSettingsDir "\" subdomain "\.key"
        if FileExist(keyFilePath) {
            try {
                FileDelete(keyFilePath)
            } catch as err {
                logError(err)
            }
        }
    }
}

getTimeStamp() {
    ms := Format("{:03d}", A_MSec)
    return FormatTime(A_Now, "yyyy-MM-dd HH:mm:ss," ms)
}

/** @param {Error} err */
logError(err) {
    logMessage := Format(
        "{1} - ERROR - Unhandled exception`nTraceback (most recent call last):`n{2}{3}: {4}`n`n",
        getTimeStamp(),
        err.Stack,
        err.What,
        err.Message)
    FileAppend(logMessage, LogDir "\log.txt")
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
