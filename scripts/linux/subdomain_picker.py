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
        self.result = None
        self.root = None
        
    def get_existing_subdomains(self) -> List[str]:
        """Get list of existing subdomain directories."""
        if not self.user_dir.exists():
            return []
        
        subdomains = []
        for item in self.user_dir.iterdir():
            if item.is_dir():
                subdomains.append(item.name)
        return sorted(subdomains)
    
    def find_active_subdomain(self) -> Optional[str]:
        """Find subdomain with existing token file (previously used)."""
        for subdomain in self.get_existing_subdomains():
            token_file = self.user_dir / subdomain / ".token"
            if token_file.exists():
                return subdomain
        return None
    
    def show_picker(self) -> Optional[Tuple[str, str]]:
        """Show subdomain picker dialog. Returns (subdomain, passphrase) or None if cancelled."""
        self.root = tk.Tk()
        self.root.title("Fast YouTrack - Select Subdomain")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Make window stay on top and focus
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        
        # Configure style for better appearance
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Fast YouTrack", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Subdomain section
        subdomain_label = ttk.Label(main_frame, text="YouTrack Subdomain:", font=("Arial", 10, "bold"))
        subdomain_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Get existing subdomains
        existing_subdomains = self.get_existing_subdomains()
        active_subdomain = self.find_active_subdomain()
        
        # Subdomain combobox (editable)
        self.subdomain_var = tk.StringVar()
        self.subdomain_combo = ttk.Combobox(main_frame, textvariable=self.subdomain_var, 
                                          values=existing_subdomains, width=45)
        self.subdomain_combo.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Set default value
        if active_subdomain:
            self.subdomain_combo.set(active_subdomain)
        elif existing_subdomains:
            self.subdomain_combo.set(existing_subdomains[0])
        
        # Helper text
        helper_text = "Select existing or type new subdomain (e.g., 'mycompany' for mycompany.youtrack.cloud)"
        helper_label = ttk.Label(main_frame, text=helper_text, font=("Arial", 8), foreground="gray")
        helper_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Passphrase section
        passphrase_label = ttk.Label(main_frame, text="Passphrase:", font=("Arial", 10, "bold"))
        passphrase_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.passphrase_var = tk.StringVar()
        self.passphrase_entry = ttk.Entry(main_frame, textvariable=self.passphrase_var, 
                                        show="*", width=45)
        self.passphrase_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        passphrase_help = "Enter passphrase to encrypt/decrypt your YouTrack token"
        passphrase_help_label = ttk.Label(main_frame, text=passphrase_help, font=("Arial", 8), foreground="gray")
        passphrase_help_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_button.grid(row=0, column=0, padx=(0, 10))
        
        ok_button = ttk.Button(button_frame, text="OK", command=self.ok_clicked)
        ok_button.grid(row=0, column=1)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Bind Enter key to OK button
        self.root.bind('<Return>', lambda e: self.ok_clicked())
        self.root.bind('<Escape>', lambda e: self.cancel())
        
        # Set focus to subdomain field if empty, otherwise passphrase
        if not self.subdomain_var.get():
            self.subdomain_combo.focus()
        else:
            self.passphrase_entry.focus()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Run the dialog
        self.root.mainloop()
        
        return self.result
    
    def ok_clicked(self):
        """Handle OK button click."""
        subdomain = self.subdomain_var.get().strip()
        passphrase = self.passphrase_var.get().strip()
        
        # Validate inputs
        if not subdomain:
            messagebox.showerror("Error", "Subdomain is required!")
            self.subdomain_combo.focus()
            return
        
        if not passphrase:
            messagebox.showerror("Error", "Passphrase is required!")
            self.passphrase_entry.focus()
            return
        
        # Validate subdomain format (basic check)
        if not subdomain.replace('-', '').replace('_', '').isalnum():
            messagebox.showerror("Error", "Subdomain contains invalid characters!\nUse only letters, numbers, hyphens, and underscores.")
            self.subdomain_combo.focus()
            return
        
        self.result = (subdomain, passphrase)
        self.root.destroy()
    
    def cancel(self):
        """Handle cancel/close."""
        self.result = None
        self.root.destroy()


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