#!/bin/sh
# universal wrapper for Fast YouTrack that detects OS and calls appropriate run script

case "$(uname -s)" in
# windows
CYGWIN* | MINGW* | MSYS* | Windows*)
  cmd.exe /c "scripts\\win\\run.bat"
  ;;
# macOS - NOT SUPPORTED YET
Darwin*)
  if [ -f "scripts/mac/run_app.command" ]; then
    chmod +x scripts/mac/run_app.command
    ./scripts/mac/run_app.command
  else
    echo "Error: macOS launcher not found"
    exit 1
  fi
  ;;
# linux - NOT SUPPORTED YET
Linux*)
  if [ -f "scripts/linux/run_app.sh" ]; then
    chmod +x scripts/linux/run_app.sh
    ./scripts/linux/run_app.sh
  else
    echo "Error: Linux launcher not found"
    exit 1
  fi
  ;;
*)
  echo "Unsupported operating system"
  exit 1
  ;;
esac
