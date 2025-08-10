# Fast YouTrack

**Fast YouTrack** — ⚡ add spent time to YouTrack issues fast, cross‑platform.

## Quick Start

Run the universal launcher:

📁 `./`
```sh
python run.py
```

What happens when you run `python run.py`?

1. 🔎 Detects your OS and picks the right runner
2. 📦 First run setup
   - 🐍 Installs Python packages into `venv/`
   - 📁 Creates `user/`, `logs/`, `pids/`
3. ▶️ Starts the app (Tk splash covers initialization)


## Usage

After setup you can launch via `python run.py` (all platforms). On Windows, there’s also a hotkey.

### Change default hotkey (Windows)

📁 `./scripts/win/ahk/run.ahk`
```ahk
; CTRL + SHIFT + T
^+t:: {
```

These symbols `^+t` mean `CTRL+SHIFT+T`. Refer to the [AutoHotkey documentation](https://www.autohotkey.com/docs/) to customize it further.

### Guide

1. 🔐 After launching, you will be prompted for a **passphrase** (required)
   - Stored as plain text in `user/<subdomain>/.key`
   - Used to derive the encryption key for your token
2. 🌐 Select or enter your **YouTrack subdomain**
3. 🔑 Enter your **YouTrack Permanent Token**
   - Encrypted with your passphrase and saved to `user/<subdomain>/.token`
4. ✨ Enjoy!

If `.key` or `.token` is missing/invalid, a friendly error dialog is shown and the app exits cleanly.

## About

This project was created as a learning exercise and a tool for personal workflows. It’s not extraordinary but may still be useful for others. Feel free to fork, adapt, or tinker with it.
