#!/usr/bin/env python3
"""Universal wrapper for Fast YouTrack that detects OS and calls appropriate run script"""

import platform
import subprocess
import sys
import os
from pathlib import Path


def main():
    system = platform.system()
    direct_mode = "--direct" in sys.argv
    
    if system == "Windows":
        # Windows - use the existing batch script (GUI by default)
        script_path = Path("scripts/win/run.bat")
        if script_path.exists():
            subprocess.run(["cmd.exe", "/c", str(script_path)])
        else:
            print("Error: Windows launcher not found")
            sys.exit(1)
    
    elif system == "Darwin":
        # macOS - GUI by default, --direct for command line
        if direct_mode:
            # Direct command line mode
            run_direct_mode()
        else:
            # Use simple shell script (default)
            script_path = Path("scripts/mac/run.sh")
            if script_path.exists():
                subprocess.run([str(script_path)])
            else:
                print("Error: macOS launcher not found")
                print("Use --direct flag for command line mode")
                sys.exit(1)
    
    elif system == "Linux":
        # Linux - direct mode only for now
        run_direct_mode()
    
    else:
        print("Unsupported operating system")
        sys.exit(1)


def check_setup():
    """Check if initial setup is needed"""
    project_root = Path(__file__).parent
    user_dir = project_root / "user"
    venv_dir = project_root / "venv"
    
    # Check if basic setup exists
    if not user_dir.exists() or not venv_dir.exists():
        print("🔧 Initial setup required...")
        print("Running setup...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("setup", project_root / "setup.py")
        setup_module = importlib.util.module_from_spec(spec)
        old_cwd = os.getcwd()
        os.chdir(project_root)
        try:
            spec.loader.exec_module(setup_module)
            setup_module.main()
        finally:
            os.chdir(old_cwd)
        return True
    
    
    return False

def check_tkinter(venv_dir):
    # Find the correct python executable
    python_path = venv_dir / "bin" / "python"
    if not python_path.exists():
        python_path = venv_dir / "Scripts" / "python.exe"
    if not python_path.exists():
        return  # Can't check, fallback to default error

    # Actually check for tkinter
    result = subprocess.run(
        [str(python_path), "-c", "import tkinter"],
        capture_output=True
    )
    if result.returncode != 0:
        import platform
        sysname = platform.system()
        print("\n❌ tkinter (Python Tk GUI) is NOT installed in your environment.")
        if sysname == "Linux":
            print("   Install with: sudo apt-get install python3-tk  # or your distro's equivalent")
        elif sysname == "Darwin":
            print("   Try: brew install python-tk@3.13  # for Homebrew Python")
            print("   Or reinstall Python from python.org")
        elif sysname == "Windows":
            print("   Reinstall Python from https://www.python.org/ and ensure Tcl/Tk is selected.")
        else:
            print("   Please install Tkinter for your platform.")
        sys.exit(2)


def run_direct_mode():
    """Run the application directly with setup"""
    project_root = Path(__file__).parent
    venv_dir = project_root / "venv"
    main_py = project_root / "src" / "main.py"
    
    # Check setup first
    check_setup()
    
    # Check if main.py exists
    if not main_py.exists():
        print(f"Error: Main script not found: {main_py}")
        sys.exit(1)
    
    # Check for tkinter before running main.py
    check_tkinter(venv_dir)

    # Run the application
    python_path = venv_dir / "bin" / "python"
    if not python_path.exists():
        python_path = venv_dir / "Scripts" / "python.exe"
    if python_path.exists():
        # Pass through any additional arguments (excluding --direct)
        args = [arg for arg in sys.argv[1:] if arg != "--direct"]
        subprocess.run([str(python_path), str(main_py)] + args, cwd=str(project_root))
    else:
        print(f"Error: Venv python not found: {python_path}")
        sys.exit(1)



if __name__ == "__main__":
    main()