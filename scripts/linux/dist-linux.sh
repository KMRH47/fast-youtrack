#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist/linux"
TEMP_DIR="$DIST_DIR/temp"

echo -e "${BLUE}Creating Fast YouTrack Linux distribution...${NC}"

# Clean up previous distribution
echo -e "${YELLOW}Cleaning previous distribution...${NC}"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"
mkdir -p "$DIST_DIR/user"
mkdir -p "$TEMP_DIR"

# Create standalone marker
echo "1" > "$DIST_DIR/STANDALONE"

# Copy user data if it exists
echo -e "${YELLOW}Copying user data...${NC}"
if [ -d "$PROJECT_ROOT/user" ]; then
    cp -r "$PROJECT_ROOT/user"/* "$DIST_DIR/user/" 2>/dev/null || true
else
    echo -e "${YELLOW}WARNING: Source user data directory not found: $PROJECT_ROOT/user${NC}"
fi

# Setup venv if needed
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}Setting up virtual environment...${NC}"
    cd "$PROJECT_ROOT"
    python3 -m venv venv
    venv/bin/pip install -q -r requirements.txt
fi

# Install PyInstaller if needed
echo -e "${YELLOW}Checking PyInstaller...${NC}"
cd "$PROJECT_ROOT"
if ! venv/bin/pip show pyinstaller >/dev/null 2>&1; then
    echo -e "${YELLOW}Installing PyInstaller...${NC}"
    venv/bin/pip install -q pyinstaller
fi

# Create PyInstaller hook for dependency-injector
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

# Compile Python application
echo -e "${YELLOW}Compiling Python application...${NC}"
cd "$PROJECT_ROOT"

venv/bin/pyinstaller --onefile --clean \
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
    --name fast-youtrack-app \
    --distpath "$DIST_DIR" \
    --workpath "$TEMP_DIR/build" \
    --specpath "$TEMP_DIR"

# Compile subdomain picker
echo -e "${YELLOW}Compiling subdomain picker...${NC}"
venv/bin/pyinstaller --onefile --clean \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    "$PROJECT_ROOT/scripts/linux/subdomain_picker.py" \
    --name subdomain_picker \
    --distpath "$DIST_DIR" \
    --workpath "$TEMP_DIR/build" \
    --specpath "$TEMP_DIR"

# Create simple launcher script
echo -e "${YELLOW}Creating launcher script...${NC}"
cat > "$DIST_DIR/fast-youtrack" << 'EOF'
#!/bin/bash
set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create user directory
mkdir -p user

# Run subdomain picker
PICKER_RESULT=$(./subdomain_picker user)
if [ $? -ne 0 ] || [ -z "$PICKER_RESULT" ]; then
    exit 0
fi

# Parse result
SUBDOMAIN=$(echo "$PICKER_RESULT" | cut -d'|' -f1)
PASSPHRASE=$(echo "$PICKER_RESULT" | cut -d'|' -f2)

# Create subdomain directory
mkdir -p "user/$SUBDOMAIN"

# Launch app
exec ./fast-youtrack-app "$PASSPHRASE" "$SUBDOMAIN"
EOF

chmod +x "$DIST_DIR/fast-youtrack"

# Copy any additional files needed
if [ -f "$PROJECT_ROOT/README.md" ]; then
    cp "$PROJECT_ROOT/README.md" "$DIST_DIR/"
fi

# Clean up temporary files
echo -e "${YELLOW}Cleaning up...${NC}"
rm -rf "$TEMP_DIR"

echo -e "${GREEN}Distribution successfully created in $DIST_DIR${NC}"

# Create .deb package
echo -e "${BLUE}Creating .deb package...${NC}"
"$SCRIPT_DIR/create-deb.sh"

echo ""
echo -e "${BLUE}To test locally:${NC}"
echo -e "  cd $DIST_DIR"
echo -e "  ./fast-youtrack"
echo ""
echo -e "${BLUE}To install system-wide:${NC}"
echo -e "  sudo dpkg -i fast-youtrack_*.deb"
echo -e "  sudo apt-get install -f  # Fix any dependencies"
echo ""
echo -e "${BLUE}After installation, users can:${NC}"
echo -e "  - Run 'fast-youtrack' from terminal"
echo -e "  - Find 'Fast YouTrack' in applications menu"