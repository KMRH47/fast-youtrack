# Fast YouTrack

**Fast YouTrack is a simple Python application for adding spent time to YouTrack issues. Built as a personal tool to learn and experiment, it leverages AutoHotkey (AHK) for quick automation on Windows.**

## Quick Start

Run `run.bat`

📁 ./

```
./run.bat
```

## Usage

After running `./run.bat`, you can launch the program. The default hotkey is `CTRL+SHIFT+T`.

The default hotkey can be changed inside `scripts/run.ahk` under:

```ahk
; CTRL SHIFT T
^+t:: {
```

These symbols `^+t` mean `CTRL+SHIFT+T`. Refer to the [AutoHotkey documentation](https://www.autohotkey.com/docs/) to customize it further.

### Steps:

1. After launching, you will be prompted for a **passphrase**. This passphrase acts as a PIN code to encrypt your YouTrack permanent token. This feature is designed to make retrieving the token more cumbersome in environments like offices. Currently, this is not optional.

2. Input your **YouTrack domain** and **token** when prompted.

3. If successful, a new UI for adding spent time will pop up. Some details, like issue types and user info, are fetched automatically.

## About

This project was created as a learning exercise and a tool for personal workflows. It’s not extraordinary but may still be useful for others. Feel free to fork, adapt, or tinker with it.
