#!/bin/bash
set -e

# Get the project root (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Setup if needed
mkdir -p user logs pids
if [ ! -d "venv" ]; then
    python3 -m venv --system-site-packages venv
    venv/bin/pip install -q -r requirements.txt
fi

# Check if app is already running
PID_FILE="pids/python.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        # App is running, try to bring window to front
        osascript -e 'tell application "Python" to activate' 2>/dev/null || true
        exit 0
    fi
fi

# Check for existing active subdomain (token file exists = used before)
ACTIVE_SUBDOMAIN=""

for subdomain_dir in user/*/; do
    if [ -d "$subdomain_dir" ]; then
        subdomain=$(basename "$subdomain_dir")
        token_file="$subdomain_dir.token"
        if [ -f "$token_file" ]; then
            ACTIVE_SUBDOMAIN="$subdomain"
            break
        fi
    fi
done

# If no active subdomain, show picker
if [ -z "$ACTIVE_SUBDOMAIN" ]; then
    # Use osascript for native macOS dialog
    result=$(osascript << 'EOF'
-- Get existing subdomain list for default
set existingSubdomains to {}
try
    set existingSubdomains to paragraphs of (do shell script "ls user 2>/dev/null || echo ''")
end try

set defaultSubdomain to ""
if length of existingSubdomains > 0 then
    set defaultSubdomain to item 1 of existingSubdomains
end if

-- Show subdomain input dialog (allows typing new ones)
set subdomainDialog to display dialog "Enter subdomain:" default answer defaultSubdomain buttons {"Cancel", "OK"} default button "OK"
if button returned of subdomainDialog is "Cancel" then return ""

set selectedSubdomain to text returned of subdomainDialog
if selectedSubdomain is "" then
    display dialog "Subdomain required!" buttons {"OK"} default button "OK" with icon caution
    return ""
end if

return selectedSubdomain
EOF
)

    if [ -z "$result" ]; then
        exit 0
    fi

    ACTIVE_SUBDOMAIN="$result"
    
    # Create subdomain folder
    mkdir -p "user/$ACTIVE_SUBDOMAIN"
fi

# Resolve passphrase: prefer .key, otherwise prompt and persist
KEY_FILE="user/$ACTIVE_SUBDOMAIN/.key"
PASSPHRASE=""
if [ -f "$KEY_FILE" ]; then
    PASSPHRASE="$(cat "$KEY_FILE")"
fi

if [ -z "$PASSPHRASE" ]; then
    PASSPHRASE=$(osascript << 'EOF'
set dlg to display dialog "Enter passphrase:" default answer "" with hidden answer buttons {"Cancel", "OK"} default button "OK"
if button returned of dlg is "Cancel" then return ""
return text returned of dlg
EOF
)
    if [ -z "$PASSPHRASE" ]; then
        exit 0
    fi
    echo -n "$PASSPHRASE" > "$KEY_FILE"
fi

# Show splash screen
venv/bin/python -c "
import tkinter as tk
import threading
import time
import subprocess
import sys

def show_splash():
    splash = tk.Tk()
    splash.title('Fast YouTrack')
    splash.geometry('300x100')
    splash.configure(bg='#2E8B57')  # Sea green like Windows version
    splash.resizable(False, False)
    splash.attributes('-topmost', True)
    
    # Center the window
    splash.update_idletasks()
    x = (splash.winfo_screenwidth() // 2) - (300 // 2)
    y = (splash.winfo_screenheight() // 2) - (100 // 2)
    splash.geometry(f'+{x}+{y}')
    
    label = tk.Label(splash, text='Starting Fast YouTrack...', 
                    bg='#2E8B57', fg='#E0FFE0', 
                    font=('Arial', 13, 'bold'))
    label.pack(expand=True)
    
    return splash

def launch_app():
    time.sleep(0.5)  # Small delay to ensure splash shows first
    subprocess.Popen(['venv/bin/python', 'src/main.py', '$PASSPHRASE', '$ACTIVE_SUBDOMAIN'])

splash = show_splash()
app_thread = threading.Thread(target=launch_app, daemon=True)
app_thread.start()

# Auto-close splash after 3 seconds or when app likely started
splash.after(3000, splash.destroy)
splash.mainloop()
" &

echo $! > "$PID_FILE"