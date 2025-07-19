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

# Create launcher script that handles subdomain selection
echo -e "${YELLOW}Creating launcher script...${NC}"
cat > "$DIST_DIR/fast-youtrack" << 'EOF'
#!/bin/bash
set -e

# Get script directory (where this launcher is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Fast YouTrack - Linux${NC}"

# Check if app is already running
PID_FILE="fast-youtrack.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo -e "${YELLOW}Fast YouTrack is already running (PID: $PID)${NC}"
        
        # Try to focus the window
        if command -v wmctrl >/dev/null 2>&1; then
            wmctrl -a "Fast YouTrack" 2>/dev/null || true
        elif command -v xdotool >/dev/null 2>&1; then
            xdotool search --name "Fast YouTrack" windowactivate 2>/dev/null || true
        fi
        
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Check for tkinter (required for subdomain picker)
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo -e "${RED}Error: tkinter is not available!${NC}"
    echo "Please install python3-tk via your package manager and try again."
    exit 1
fi

# Function to get existing subdomains
get_existing_subdomains() {
    if [ -d "user" ]; then
        find user -maxdepth 1 -type d ! -name user -exec basename {} \; 2>/dev/null | sort
    fi
}

# Function to find active subdomain (has token file)
find_active_subdomain() {
    for subdomain_dir in user/*/; do
        if [ -d "$subdomain_dir" ]; then
            subdomain=$(basename "$subdomain_dir")
            token_file="$subdomain_dir/.token"
            if [ -f "$token_file" ]; then
                echo "$subdomain"
                return 0
            fi
        fi
    done
    return 1
}

# Simple subdomain picker using Python/tkinter
get_subdomain_and_passphrase() {
    python3 << 'PYTHON_EOF'
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

class SubdomainPicker:
    def __init__(self):
        self.result = None
        
    def get_existing_subdomains(self):
        if not os.path.exists('user'):
            return []
        subdomains = []
        for item in os.listdir('user'):
            if os.path.isdir(os.path.join('user', item)):
                subdomains.append(item)
        return sorted(subdomains)
    
    def find_active_subdomain(self):
        for subdomain in self.get_existing_subdomains():
            token_file = os.path.join('user', subdomain, '.token')
            if os.path.exists(token_file):
                return subdomain
        return None
    
    def show_picker(self):
        root = tk.Tk()
        root.title("Fast YouTrack - Select Subdomain")
        root.geometry("400x250")
        root.resizable(False, False)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (400 // 2)
        y = (root.winfo_screenheight() // 2) - (250 // 2)
        root.geometry(f"+{x}+{y}")
        
        root.attributes("-topmost", True)
        root.focus_force()
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Fast YouTrack", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Subdomain
        ttk.Label(main_frame, text="YouTrack Subdomain:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        subdomain_var = tk.StringVar()
        subdomain_combo = ttk.Combobox(main_frame, textvariable=subdomain_var, 
                                     values=self.get_existing_subdomains(), width=50)
        subdomain_combo.pack(fill=tk.X, pady=(5, 10))
        
        # Set default
        active = self.find_active_subdomain()
        if active:
            subdomain_combo.set(active)
        elif self.get_existing_subdomains():
            subdomain_combo.set(self.get_existing_subdomains()[0])
        
        # Passphrase
        ttk.Label(main_frame, text="Passphrase:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        passphrase_var = tk.StringVar()
        passphrase_entry = ttk.Entry(main_frame, textvariable=passphrase_var, show="*", width=50)
        passphrase_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        def ok_clicked():
            subdomain = subdomain_var.get().strip()
            passphrase = passphrase_var.get().strip()
            
            if not subdomain:
                messagebox.showerror("Error", "Subdomain is required!")
                return
            if not passphrase:
                messagebox.showerror("Error", "Passphrase is required!")
                return
                
            self.result = (subdomain, passphrase)
            root.destroy()
        
        def cancel():
            root.destroy()
        
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="OK", command=ok_clicked).pack(side=tk.LEFT)
        
        # Bindings
        root.bind('<Return>', lambda e: ok_clicked())
        root.bind('<Escape>', lambda e: cancel())
        
        # Focus
        if not subdomain_var.get():
            subdomain_combo.focus()
        else:
            passphrase_entry.focus()
        
        root.protocol("WM_DELETE_WINDOW", cancel)
        root.mainloop()
        
        return self.result

picker = SubdomainPicker()
result = picker.show_picker()

if result:
    subdomain, passphrase = result
    print(f"{subdomain}|{passphrase}")
    sys.exit(0)
else:
    sys.exit(1)
PYTHON_EOF
}

# Get subdomain and passphrase
echo -e "${BLUE}Opening subdomain picker...${NC}"
PICKER_RESULT=$(get_subdomain_and_passphrase)
if [ $? -ne 0 ] || [ -z "$PICKER_RESULT" ]; then
    echo -e "${YELLOW}Cancelled by user.${NC}"
    exit 0
fi

# Parse result
SUBDOMAIN=$(echo "$PICKER_RESULT" | cut -d'|' -f1)
PASSPHRASE=$(echo "$PICKER_RESULT" | cut -d'|' -f2)

# Create subdomain directory
mkdir -p "user/$SUBDOMAIN"

echo -e "${GREEN}Starting Fast YouTrack for $SUBDOMAIN...${NC}"

# Launch the application
./fast-youtrack-app "$PASSPHRASE" "$SUBDOMAIN" &
APP_PID=$!

# Save PID
echo $APP_PID > "$PID_FILE"

# Quick check if app started
sleep 1
if ! kill -0 "$APP_PID" 2>/dev/null; then
    echo -e "${RED}Error: Application failed to start${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

echo -e "${GREEN}Fast YouTrack started successfully!${NC}"
EOF

# Make launcher executable
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