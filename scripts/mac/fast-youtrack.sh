#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Fast YouTrack
# @raycast.mode fullOutput
# @raycast.icon 🤖
# @raycast.description add time fast


#!/bin/bash
set -euo pipefail

# Use BASH_SOURCE[0] for robustness in some execution contexts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

VENV_DIR="$PROJECT_ROOT/venv"
MAIN_PY="$PROJECT_ROOT/src/main.py"

echo "[bootstrap] Running from PROJECT_ROOT: $PROJECT_ROOT" # Added for debug

# 1. ensure Tk present
# Added some error handling for brew and clarification
python3 - <<'PY' || {
import sys, subprocess, shutil, os
try:
    import tkinter; sys.exit(0)
except ImportError:
    pass
print("[bootstrap] _tkinter missing – attempting install via brew python-tk@3.13…")
# Check if brew is available before attempting to run it
if not shutil.which("brew"):
    print("[bootstrap] Error: 'brew' command not found. Cannot install python-tk.")
    print("[bootstrap] Please install Homebrew (https://brew.sh) or install python-tk manually for your system's Python.")
    sys.exit(1) # Exit indicates prerequisite failure

try:
    # Note: '@3.13' is specific to brew's python@3.13. If using another python3, this might differ.
    print("Running: brew install python-tk@3.13")
    subprocess.run(["brew", "install", "python-tk@3.13"], check=True)
    print("[bootstrap] python-tk installed successfully.")
    # Successfully installed, now signal the outer script to re-run
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"[bootstrap] Failed to install python-tk: {e}", file=sys.stderr)
    sys.exit(1) # Installation failed
except Exception as e:
    print(f"[bootstrap] An unexpected error occurred during installation attempt: {e}", file=sys.stderr)
    sys.exit(1)

PY
# If the python block exited with 1 (meaning install needed or failed),
# and brew install was *attempted* (exit code from subprocess.run >=0),
# then re-run the script to pick up the changes or report failure.
# The 'exec' command replaces the current process, effectively restarting the script.
# If the python block successfully installed and exited with 1, the exec runs again.
# If the python block found Tk and exited with 0, this check fails, and script continues.
# If brew failed inside the python block, python block exits with 1, and the exec will just fail again immediately.
# Let's refine the exit logic here slightly for clarity:
# If python script exits with 1, it means install was needed OR install failed.
# We only want to re-exec if the install *might* have succeeded.
# A simpler check is just the exit code == 1 from the initial python block.
# If it exited 1 because brew *failed*, the re-run will likely also fail, but that's okay,
# the user will see the brew errors from the previous attempt.
(( $? == 1 )) && { echo "[bootstrap] python-tk installation likely attempted. Re-running script to confirm..."; exec "$0" "$@"; }
# Note: If the above `exec` line was reached because `brew install` *failed* (subprocess.CalledProcessError inside PY block),
# the subsequent re-run will hit the PY block again, fail the Tkinter import again, and try brew again,
# potentially looping on a failed install. However, given the prompt's "crashes instantly", the assumption
# is that the Tk check *passes* or the brew install *succeeds* and the issue is *after* this.

# 2. venv with system-site-packages (inherits Tk)
if [[ ! -d "$VENV_DIR" ]]; then
  echo "[bootstrap] creating Tk-aware venv '$VENV_DIR'…"
  # Ensure a python3 command is found
  PYTHON3_CMD=$(command -v python3 || command -v /usr/bin/python3 || echo "") # Attempt to find python3
  if [[ -z "$PYTHON3_CMD" ]]; then
     echo "[bootstrap] Error: Could not find a working 'python3' command to create the virtual environment." >&2
     exit 1
  fi

  "$PYTHON3_CMD" -m venv --system-site-packages "$VENV_DIR" || { echo "[bootstrap] Failed to create venv. Ensure python3 is available and has venv module."; exit 1; }
  echo "[bootstrap] Installing dependencies from requirements.txt…"
  # Use the explicit path to pip within the newly created venv
  "$VENV_DIR/bin/pip" install -q -r "$PROJECT_ROOT/requirements.txt" || { echo "[bootstrap] Failed to install dependencies."; exit 1; }
  echo "[bootstrap] Venv setup complete."
fi

# 3. run app - using direct execution
echo "[bootstrap] Checking for venv python executable..."
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    echo "[bootstrap] Error: Venv python executable not found or not executable: '$VENV_DIR/bin/python'" >&2
    echo "[bootstrap] Check venv creation step." >&2
    exit 1
fi

echo "[bootstrap] Checking for main script..."
if [[ ! -f "$MAIN_PY" ]]; then
    echo "[bootstrap] Error: Main script not found: '$MAIN_PY'" >&2
    exit 1
fi

echo "[bootstrap] Changing directory to project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT" || { echo "[bootstrap] Failed to change directory to project root '$PROJECT_ROOT'"; exit 1; }

echo "[bootstrap] Executing app using venv python: $VENV_DIR/bin/python $MAIN_PY"
# Execute the main script using the venv's python
# This replaces the 'source ... && python ...' logic
"$VENV_DIR/bin/python" "$MAIN_PY"

echo "[bootstrap] Script finished." # Only reaches here if the python script exits gracefully