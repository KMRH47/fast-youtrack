#!/usr/bin/env python3
"""
Linux subdomain picker using tkinter.
Provides GUI for selecting existing subdomains or entering new ones.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Tuple, List


class SubdomainPicker:
    def __init__(self, user_dir: Path):
        self.user_dir = user_dir
        self.result: Optional[Tuple[str, str]] = None
        self.root: Optional[tk.Tk] = None
        self.subdomain_var: Optional[tk.StringVar] = None
        self.passphrase_var: Optional[tk.StringVar] = None

    def get_existing_subdomains(self) -> List[str]:
        if not self.user_dir.exists():
            return []
        return sorted(d.name for d in self.user_dir.iterdir() if d.is_dir())

    def find_active_subdomain(self) -> Optional[str]:
        for subdomain in self.get_existing_subdomains():
            if (self.user_dir / subdomain / ".token").exists():
                return subdomain
        return None

    def _setup_vars(self) -> None:
        subdomains = self.get_existing_subdomains()
        active = self.find_active_subdomain()
        default_sub = active or (subdomains[0] if subdomains else "")
        self.subdomain_var.set(default_sub)

    def _build_ui(self) -> ttk.Frame:
        root = self.root
        frame = ttk.Frame(root, padding="20")
        frame.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        ttk.Label(frame, text="Fast YouTrack", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )
        ttk.Label(frame, text="YouTrack Subdomain:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w"
        )
        self.subdomain_combo = ttk.Combobox(
            frame,
            textvariable=self.subdomain_var,
            values=self.get_existing_subdomains(),
            width=45,
        )
        self.subdomain_combo.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(0, 5)
        )
        ttk.Label(
            frame,
            text="Select existing or type new subdomain (e.g., 'mycompany' for mycompany.youtrack.cloud)",
            font=("Arial", 8),
            foreground="gray",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 15))
        ttk.Label(frame, text="Passphrase:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, columnspan=2, sticky="w"
        )
        self.passphrase_entry = ttk.Entry(
            frame, textvariable=self.passphrase_var, show="*", width=45
        )
        self.passphrase_entry.grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(0, 5)
        )
        ttk.Label(
            frame,
            text="Enter passphrase to encrypt/decrypt your YouTrack token",
            font=("Arial", 8),
            foreground="gray",
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 20))
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=lambda: self._cancel()).grid(
            row=0, column=0, padx=(0, 10)
        )
        ttk.Button(button_frame, text="OK", command=lambda: self._ok()).grid(
            row=0, column=1
        )
        frame.columnconfigure(1, weight=1)
        return frame

    def _bind_events(self) -> None:
        self.root.bind("<Return>", lambda e: self._ok())
        self.root.bind("<KP_Enter>", lambda e: self._ok())
        self.root.bind("<Escape>", lambda e: self._cancel())
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)

    def _validate(self) -> Optional[str]:
        subdomain = self.subdomain_var.get().strip()
        passphrase = self.passphrase_var.get().strip()
        if not subdomain:
            return "Subdomain is required!"
        if not passphrase:
            return "Passphrase is required!"
        if not subdomain.replace("-", "").replace("_", "").isalnum():
            return "Subdomain contains invalid characters!\nUse only letters, numbers, hyphens, and underscores."
        return None

    def _ok(self) -> None:
        error = self._validate()
        if error:
            messagebox.showerror("Error", error)
            return
        self.result = (
            self.subdomain_var.get().strip(),
            self.passphrase_var.get().strip(),
        )
        self.root.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.root.destroy()

    def show_picker(self) -> Optional[Tuple[str, str]]:
        import sys
        import os

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
        from utils.window_utils import center_window_on_primary_monitor

        self.root = tk.Tk()
        self.root.title("Fast YouTrack - Select Subdomain")
        center_window_on_primary_monitor(self.root, 400, 300)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.subdomain_var = tk.StringVar()
        self.passphrase_var = tk.StringVar()

        self._setup_vars()
        self._build_ui()
        self._bind_events()

        # Focus logic: subdomain if empty, else passphrase
        if not self.subdomain_var.get():
            self.subdomain_combo.focus_set()
        else:
            self.passphrase_entry.focus_set()

        self.root.mainloop()
        return self.result


def main():
    """Main entry point for subdomain picker."""
    if len(sys.argv) != 2:
        print("Usage: subdomain_picker.py <user_directory>", file=sys.stderr)
        sys.exit(1)

    user_dir = Path(sys.argv[1])
    picker = SubdomainPicker(user_dir)
    result = picker.show_picker()

    if result:
        subdomain, passphrase = result
        print(f"{subdomain}|{passphrase}")
        sys.exit(0)
    else:
        sys.exit(1)  # Cancelled


if __name__ == "__main__":
    main()
