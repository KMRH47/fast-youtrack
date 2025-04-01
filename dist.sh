#!/bin/sh
# universal wrapper for Fast YouTrack distribution that detects OS and calls appropriate dist script

case "$(uname -s)" in
# windows
CYGWIN* | MINGW* | MSYS* | Windows*)
  echo "Creating Windows distribution..."
  cmd.exe /c "scripts\\win\\dist-win.bat"
  ;;
# macOS - NOT SUPPORTED YET
Darwin*)
  echo "Creating macOS distribution..."
  if [ -f "scripts/mac/dist-mac.sh" ]; then
    chmod +x scripts/mac/dist-mac.sh
    ./scripts/mac/dist-mac.sh
  else
    echo "Error: macOS distribution script not found"
    exit 1
  fi
  ;;
# linux - NOT SUPPORTED YET
Linux*)
  echo "Creating Linux distribution..."
  if [ -f "scripts/linux/dist-linux.sh" ]; then
    chmod +x scripts/linux/dist-linux.sh
    ./scripts/linux/dist-linux.sh
  else
    echo "Error: Linux distribution script not found"
    exit 1
  fi
  ;;
*)
  echo "Unsupported operating system"
  exit 1
  ;;
esac
