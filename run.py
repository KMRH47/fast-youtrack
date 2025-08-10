import platform
import subprocess
import sys
import os
from pathlib import Path


def main() -> None:
    system = platform.system()
    direct_mode = "--direct" in sys.argv

    if system == "Windows":
        _run_windows()
        return

    if system == "Darwin":
        if direct_mode:
            run_direct_mode()
        else:
            _run_shell(Path("scripts/mac/run.sh"), "macOS")
        return

    if system == "Linux":
        if direct_mode:
            run_direct_mode()
        else:
            _run_shell(Path("scripts/linux/run.sh"), "Linux")
        return

    print("Unsupported operating system")
    sys.exit(1)


def check_setup() -> bool:
    """Run setup on first launch (venv + user dirs)."""
    project_root = Path(__file__).parent
    user_dir = project_root / "user"
    venv_dir = project_root / "venv"

    if not user_dir.exists() or not venv_dir.exists():
        print("🔧 Initial setup required...")
        print("Running setup...")
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "setup", project_root / "setup.py"
        )
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


def check_tkinter(venv_dir: Path) -> None:
    python_path = venv_dir / "bin" / "python"
    if not python_path.exists():
        python_path = venv_dir / "Scripts" / "python.exe"
    if not python_path.exists():
        return

    result = subprocess.run(
        [str(python_path), "-c", "import tkinter"], capture_output=True
    )
    if result.returncode != 0:
        sysname = platform.system()
        print("\n❌ tkinter (Python Tk GUI) is NOT installed in your environment.")
        if sysname == "Linux":
            distro_id = None
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            distro_id = line.strip().split("=")[1].strip('"')
                            break
            except Exception:
                pass
            if distro_id in ("ubuntu", "debian", "linuxmint"):
                print("   Install with: sudo apt-get install python3-tk")
            elif distro_id == "fedora":
                print("   Install with: sudo dnf install python3-tkinter")
            elif distro_id == "arch":
                print("   Install with: sudo pacman -S tk")
            elif distro_id in ("centos", "rhel"):
                print("   Install with: sudo yum install tkinter")
            else:
                print("   Please install python3-tk via your package manager.")
        elif sysname == "Darwin":
            print("   Try: brew install python-tk@3.13  # for Homebrew Python")
            print("   Or reinstall Python from python.org")
        elif sysname == "Windows":
            print(
                "   Reinstall Python from https://www.python.org/ and ensure Tcl/Tk is selected."
            )
        else:
            print("   Please install Tkinter for your platform.")
        sys.exit(2)


def run_direct_mode() -> None:
    """Run the application directly with setup."""
    project_root = Path(__file__).parent
    venv_dir = project_root / "venv"
    main_py = project_root / "src" / "main.py"

    check_setup()

    if not main_py.exists():
        print(f"Error: Main script not found: {main_py}")
        sys.exit(1)

    check_tkinter(venv_dir)

    python_path = venv_dir / "bin" / "python"
    if not python_path.exists():
        python_path = venv_dir / "Scripts" / "python.exe"
    if python_path.exists():
        args = [arg for arg in sys.argv[1:] if arg != "--direct"]
        subprocess.run([str(python_path), str(main_py)] + args, cwd=str(project_root))
    else:
        print(f"Error: Venv python not found: {python_path}")
        sys.exit(1)


def _run_windows() -> None:
    script_path = Path("scripts/win/run.bat")
    if script_path.exists():
        subprocess.run(["cmd.exe", "/c", str(script_path)])
    else:
        print("Error: Windows launcher not found")
        sys.exit(1)


def _run_shell(path: Path, label: str) -> None:
    if path.exists():
        subprocess.run([str(path)])
    else:
        print(f"Error: {label} launcher not found at {path}")
        print("Use --direct flag for command line mode")
        sys.exit(1)


if __name__ == "__main__":
    main()
