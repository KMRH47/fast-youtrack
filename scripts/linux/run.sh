#!/bin/bash
set -e

# Get the project root (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Fast YouTrack - Linux${NC}"
echo "=================================="

# Setup if needed
mkdir -p user logs pids
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Setting up virtual environment...${NC}"
    python3 -m venv venv
    venv/bin/pip install -q -r requirements.txt
    echo -e "${GREEN}Virtual environment created.${NC}"
fi

# Check if app is already running
PID_FILE="pids/python.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo -e "${YELLOW}Fast YouTrack is already running (PID: $PID)${NC}"
        echo "Attempting to bring window to front..."
        
        # Try to focus the window using various methods
        if command -v wmctrl >/dev/null 2>&1; then
            wmctrl -a "Fast YouTrack" 2>/dev/null || true
        elif command -v xdotool >/dev/null 2>&1; then
            xdotool search --name "Fast YouTrack" windowactivate 2>/dev/null || true
        fi
        
        exit 0
    else
        # Process not running, remove stale PID file
        rm -f "$PID_FILE"
    fi
fi

# Check for tkinter
echo -e "${BLUE}Checking tkinter availability...${NC}"
if ! venv/bin/python -c "import tkinter" 2>/dev/null; then
    echo -e "${RED}Error: tkinter is not available!${NC}"
    echo "tkinter is required for the GUI. Please install it:"
    echo ""
    
    # Detect distribution and provide specific instructions
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian|linuxmint)
                echo -e "${YELLOW}  sudo apt-get install python3-tk${NC}"
                ;;
            fedora)
                echo -e "${YELLOW}  sudo dnf install python3-tkinter${NC}"
                ;;
            arch|manjaro)
                echo -e "${YELLOW}  sudo pacman -S tk${NC}"
                ;;
            centos|rhel)
                echo -e "${YELLOW}  sudo yum install tkinter${NC}"
                ;;
            *)
                echo -e "${YELLOW}  Install python3-tk via your package manager${NC}"
                ;;
        esac
    else
        echo -e "${YELLOW}  Install python3-tk via your package manager${NC}"
    fi
    
    exit 1
fi

# Function to check for active subdomain
get_active_subdomain() {
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

# Always use GUI picker for consistency
echo -e "${BLUE}Opening subdomain picker...${NC}"

# Run the subdomain picker
PICKER_RESULT=$(venv/bin/python "scripts/linux/subdomain_picker.py" "user" 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$PICKER_RESULT" ]; then
    echo -e "${YELLOW}Cancelled by user.${NC}"
    exit 0
fi

# Parse result (format: subdomain|passphrase)
ACTIVE_SUBDOMAIN=$(echo "$PICKER_RESULT" | cut -d'|' -f1)
PASSPHRASE=$(echo "$PICKER_RESULT" | cut -d'|' -f2)

# Create subdomain directory if it doesn't exist
mkdir -p "user/$ACTIVE_SUBDOMAIN"

echo -e "${GREEN}Selected subdomain: $ACTIVE_SUBDOMAIN${NC}"

# Validate we have both subdomain and passphrase
if [ -z "$ACTIVE_SUBDOMAIN" ] || [ -z "$PASSPHRASE" ]; then
    echo -e "${RED}Error: Missing subdomain or passphrase${NC}"
    exit 1
fi

# Show a brief loading message
echo -e "${BLUE}Starting Fast YouTrack...${NC}"

# Launch the application with proper arguments
# The application expects: python main.py <passphrase> <subdomain>
venv/bin/python src/main.py "$PASSPHRASE" "$ACTIVE_SUBDOMAIN" &
APP_PID=$!

# Save PID for future reference
echo $APP_PID > "$PID_FILE"

# Brief pause to see if app starts successfully
sleep 1
if ! kill -0 "$APP_PID" 2>/dev/null; then
    echo -e "${RED}Error: Application failed to start${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

echo -e "${GREEN}Fast YouTrack started successfully (PID: $APP_PID)${NC}"
echo "Use Ctrl+C to stop monitoring, or check logs/app.log for details"

# Optional: Wait for the process (comment out if you want script to exit immediately)
# wait $APP_PID
# rm -f "$PID_FILE"