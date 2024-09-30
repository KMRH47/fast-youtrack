#Requires AutoHotkey v2.0

/** @param {String} dir
 *  Get all folder names in the given directory. */
GetFolderNames(dir) {
    folderNames := []

    loop files, dir "\*", "D" {
        folderName := A_LoopFileName
        if (folderName) {
            folderNames.Push(folderName)
        }
    }
    return folderNames
}

/** @param {Error} err
 * @param {String} fileName
 * The name of the file to be appended.
 * If the absolute path is not specified, it is assumed to be in A_WorkingDir.
 * The target directory must already exist.
 * Standard output (stdout): Specify an asterisk (*) in FileName to send Text to standard output (stdout).
 * Specify two asterisks (**) in FileName to send Text to standard error output (stderr).
 * */
LogError(err, fileName) {
    logMessage := Format(
        "{1} - ERROR - Unhandled exception`nTraceback (most recent call last):`n{2}{3}: {4}`n`n",
        GetTimeStamp(),
        err.Stack,
        err.What,
        err.Message)
    FileAppend(logMessage, fileName)
}

GetTimeStamp() {
    ms := Format("{:03d}", A_MSec)
    return FormatTime(A_Now, "yyyy-MM-dd HH:mm:ss," ms)
}
