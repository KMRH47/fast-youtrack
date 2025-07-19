#!/bin/bash
# Fast YouTrack - Linux Launcher
# Simple wrapper to launch Fast YouTrack on Linux

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use the universal Python launcher
python3 run.py