#!/bin/bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist/macos"
TEMP_DIR="$DIST_DIR/temp"

echo -e "${BLUE}Creating Fast YouTrack macOS distribution...${NC}"

# Clean previous
echo -e "${YELLOW}Cleaning previous distribution...${NC}"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/user"
mkdir -p "$TEMP_DIR"

# Standalone marker
echo "1" > "$DIST_DIR/STANDALONE"

# Copy user data if present
echo -e "${YELLOW}Copying user data...${NC}"
if [ -d "$PROJECT_ROOT/user" ]; then
  cp -R "$PROJECT_ROOT/user/." "$DIST_DIR/user/" 2>/dev/null || true
else
  echo -e "${YELLOW}WARNING: Source user data directory not found: $PROJECT_ROOT/user${NC}"
fi

# Python venv
if [ ! -d "$PROJECT_ROOT/venv" ]; then
  echo -e "${YELLOW}Setting up virtual environment...${NC}"
  cd "$PROJECT_ROOT"
  python3 -m venv venv
  "venv/bin/pip" install -q -r requirements.txt
fi

# PyInstaller
echo -e "${YELLOW}Checking PyInstaller...${NC}"
cd "$PROJECT_ROOT"
if ! "venv/bin/pip" show pyinstaller >/dev/null 2>&1; then
  echo -e "${YELLOW}Installing PyInstaller...${NC}"
  "venv/bin/pip" install -q pyinstaller
fi

# Hook for dependency_injector
echo -e "${YELLOW}Creating PyInstaller hooks...${NC}"
cat > "$TEMP_DIR/hook-dependency_injector.py" << 'EOF'
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

hiddenimports = collect_submodules('dependency_injector')
hiddenimports += [
    'dependency_injector.errors',
    'dependency_injector.wiring',
    'dependency_injector.providers',
    'dependency_injector.containers',
    'dependency_injector._declarations',
    'dependency_injector._containers',
    'dependency_injector.providers.singleton',
    'dependency_injector.providers.factory',
    'dependency_injector._utils',
    'dependency_injector.cpp_utils',
    'dependency_injector.providers_types',
]

datas = collect_data_files('dependency_injector')
datas += copy_metadata('dependency_injector')
EOF

# Build main app (.app bundle, GUI)
echo -e "${YELLOW}Compiling Python application (.app)...${NC}"
cd "$PROJECT_ROOT"
"venv/bin/pyinstaller" --clean --onefile --windowed \
  --paths="$PROJECT_ROOT" \
  --paths="$PROJECT_ROOT/src" \
  --additional-hooks-dir="$TEMP_DIR" \
  --hidden-import=dependency_injector.errors \
  --hidden-import=dependency_injector.wiring \
  --hidden-import=dependency_injector._utils \
  --hidden-import=dependency_injector.providers \
  --hidden-import=dependency_injector.containers \
  --hidden-import=dependency_injector.cpp_utils \
  --hidden-import=tkinter \
  --hidden-import=tkinter.ttk \
  "$PROJECT_ROOT/src/main.py" \
  --name FastYouTrack \
  --distpath "$DIST_DIR" \
  --workpath "$TEMP_DIR/build" \
  --specpath "$TEMP_DIR"

# Build subdomain picker (console exe to capture stdout)
echo -e "${YELLOW}Compiling subdomain picker...${NC}"
"venv/bin/pyinstaller" --onefile --clean \
  --paths="$PROJECT_ROOT" \
  --paths="$PROJECT_ROOT/src" \
  --hidden-import=tkinter \
  --hidden-import=tkinter.ttk \
  "$PROJECT_ROOT/scripts/linux/subdomain_picker.py" \
  --name subdomain_picker \
  --distpath "$DIST_DIR" \
  --workpath "$TEMP_DIR/build" \
  --specpath "$TEMP_DIR"

# Launcher script to glue picker and app together
echo -e "${YELLOW}Creating launcher script...${NC}"
cat > "$DIST_DIR/fast-youtrack-mac" << 'EOF'
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p user

PICKER_RESULT="$(./subdomain_picker user || true)"
if [ -z "$PICKER_RESULT" ]; then
  exit 0
fi

SUBDOMAIN="$(echo "$PICKER_RESULT" | cut -d'|' -f1)"
PASSPHRASE="$(echo "$PICKER_RESULT" | cut -d'|' -f2)"

mkdir -p "user/$SUBDOMAIN"

# Persist passphrase for subsequent runs (mirrors Windows AHK behavior)
echo -n "$PASSPHRASE" > "user/$SUBDOMAIN/.key"

APP_BIN="$SCRIPT_DIR/FastYouTrack.app/Contents/MacOS/FastYouTrack"
if [ ! -x "$APP_BIN" ]; then
  echo "Error: App binary not found at $APP_BIN" >&2
  exit 1
fi

exec "$APP_BIN" "$PASSPHRASE" "$SUBDOMAIN"
EOF

chmod +x "$DIST_DIR/fast-youtrack-mac"

# Write environment file for overrides (optional)
cat > "$DIST_DIR/.env" << 'EOF'
# Override base dir if needed
# FAST_YOUTRACK_BASE_DIR="/absolute/path/to/user/<subdomain>"
EOF

# Copy README if present
if [ -f "$PROJECT_ROOT/README.md" ]; then
  cp "$PROJECT_ROOT/README.md" "$DIST_DIR/"
fi

# Cleanup temp
echo -e "${YELLOW}Cleaning up...${NC}"
rm -rf "$TEMP_DIR"

echo -e "${GREEN}Distribution successfully created in $DIST_DIR${NC}"
echo
echo -e "${BLUE}To test locally:${NC}"
echo -e "  cd $DIST_DIR"
echo -e "  ./fast-youtrack-mac"
echo

