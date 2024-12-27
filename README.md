# Fast YouTrack

**Fast YouTrack is a simple Python application for adding spent time to YouTrack issues. Built as a personal tool to learn and experiment, it leverages AutoHotkey (AHK) for quick automation on Windows.**

## Quick Start

Run `run.bat`

📁 `./`
```sh
./run.bat
```

*What happens when you run* `./run.bat`?

1. 🔎 Checks if Python is installed
2. 📦 Sets up everything you need (first time only)
    - 🐍 Python packages
    - ⌨️ AutoHotkey v2 portable
3. ▶️ Starts the app in background


## Usage

After running `./run.bat`, you can launch the program. The default hotkey is `CTRL+SHIFT+T`.

### Change default hotkey

📁 `./scripts/run.ahk`
```ahk
; CTRL SHIFT T
^+t:: {
```

These symbols `^+t` mean `CTRL+SHIFT+T`. Refer to the [AutoHotkey documentation](https://www.autohotkey.com/docs/) to customize it further.

### Guide

1. 🔎 After launching, you will be prompted for a **passphrase**

⚠️ **The passphrase is stored in plain text**

*This passphrase acts as a PIN code to encrypt your YouTrack permanent token. This feature is designed to make retrieving the token more cumbersome in environments like offices. Currently, this is not optional.*

2. 🌐 Input your **YouTrack domain**
3. 🔑 Input your **YouTrack token**
4. ✨ Enjoy!

## About

This project was created as a learning exercise and a tool for personal workflows. It’s not extraordinary but may still be useful for others. Feel free to fork, adapt, or tinker with it.
