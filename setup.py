#!/usr/bin/env python3
"""Cross-platform setup script for Fast YouTrack"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def main() -> None:
    """Main setup function"""
    print("Fast YouTrack Setup")
    print("=" * 50)

    project_root = Path.cwd()

    setup_directories(project_root)

    setup_venv(project_root)

    system = platform.system()
    if system == "Darwin":
        setup_macos(project_root)
    elif system == "Windows":
        setup_windows(project_root)
    elif system == "Linux":
        setup_linux(project_root)

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Add your YouTrack subdomain folders to the 'user' directory")
    print("2. Run: python3 run.py")

    if system == "Darwin":
        print("3. Optional: Run scripts/mac/setup-hotkey.applescript for global hotkey")


def setup_directories(project_root: Path) -> None:
    """Create necessary directories"""
    print("\n📁 Setting up directories...")

    directories = ["user", "logs", "pids"]

    for dir_name in directories:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"   ✓ {dir_name}/")


def setup_venv(project_root: Path) -> None:
    """Setup Python virtual environment and dependencies"""
    print("\n🐍 Setting up Python environment...")

    venv_dir = project_root / "venv"
    requirements_file = project_root / "requirements.txt"

    try:
        result = subprocess.run(
            [sys.executable, "--version"], capture_output=True, text=True, check=True
        )
        print(f"   ✓ Using Python: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("   ❌ Python not found!")
        sys.exit(1)

    if not venv_dir.exists():
        print("   📦 Creating virtual environment...")
        try:
            _ = subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir)], check=True
            )
            print("   ✓ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create virtual environment: {e}")
            sys.exit(1)
    else:
        print("   ✓ Virtual environment already exists")

    if requirements_file.exists():
        print("   📥 Installing dependencies...")
        pip_path = venv_dir / (
            "Scripts/pip.exe" if platform.system() == "Windows" else "bin/pip"
        )

        try:
            _ = subprocess.run(
                [str(pip_path), "install", "-q", "-r", str(requirements_file)],
                check=True,
            )
            print("   ✓ Dependencies installed")

            system = platform.system()
            if system == "Darwin":
                macos_requirements = project_root / "requirements-macos.txt"
                if macos_requirements.exists():
                    _ = subprocess.run(
                        [str(pip_path), "install", "-q", "-r", str(macos_requirements)],
                        check=True,
                    )
                    print("   ✓ macOS-specific dependencies installed")

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            sys.exit(1)
    else:
        print("   ⚠️  No requirements.txt found")


def setup_macos(project_root: Path) -> None:
    print("\n🍎 macOS setup...")

    print("   🔍 Checking for tkinter...")
    try:
        _ = subprocess.run(
            [sys.executable, "-c", "import tkinter"], check=True, capture_output=True
        )
        print("   ✓ tkinter available")
    except subprocess.CalledProcessError:
        print("   ❌ tkinter NOT FOUND")
        print("   This application REQUIRES tkinter, which is not available.")
        print("   If you use Homebrew Python, run: brew install python-tk@3.13")
        print("   Or reinstall Python from python.org (includes tkinter by default).")
        sys.exit(2)

    script_dir = project_root / "scripts" / "mac"
    if script_dir.exists():
        for script_file in script_dir.glob("*.applescript"):
            os.chmod(script_file, 0o755)
            print(f"   ✓ Made executable: {script_file.name}")


def setup_windows(_project_root: Path) -> None:
    """Windows-specific setup (mostly handled by existing .bat files)"""
    print("\n🪟 Windows setup...")
    print("   ✓ Windows setup handled by existing batch files")


def setup_linux(_project_root: Path) -> None:
    print("\n🐧 Linux setup...")

    print("   🔍 Checking for tkinter...")
    try:
        _ = subprocess.run(
            [sys.executable, "-c", "import tkinter"], check=True, capture_output=True
        )
        print("   ✓ tkinter available")
    except subprocess.CalledProcessError:
        print("   ❌ tkinter NOT FOUND")
        print("   This application REQUIRES tkinter, which is not installed.")
        print("   Install it and re-run setup:")
        print("      sudo apt-get install python3-tk       # Ubuntu/Debian")
        print("      sudo dnf install python3-tkinter       # Fedora")
        print("      sudo pacman -S tk                      # Arch")
        print("      sudo yum install tkinter               # CentOS/RHEL")
        sys.exit(2)


if __name__ == "__main__":
    main()
