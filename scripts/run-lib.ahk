#Requires AutoHotkey v2.0

/** @param {String} baseDir
 *  Recursively search for all user-config.yaml files */
GetSubdomains(baseDir) {
    subdomains := []

    loop files, baseDir "\**\user-config.yaml", "R" {
        subdomain := ExtractSubdomain(A_LoopFileFullPath)
        if (subdomain) {
            subdomains.Push(subdomain)
        }
    }
    return subdomains
}

/** @param {String} configFile */
ExtractSubdomain(configFilePath) {
    fileContent := FileRead(configFilePath)
    match := {}
    if RegExMatch(fileContent, "subdomain:\s*(.+)", &match) {
        return match.1
    }
    return ""
}

/** @param {String} ExitReason
 *  @param {Number} ExitCode */
DeleteKeyFile(ExitReason, ExitCode) {
    if FileExist(KeyFile) {
        FileDelete(KeyFile)
    }
}
