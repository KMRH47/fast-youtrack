from typing import Optional
from pydantic import ValidationError
from models.credentials import Credentials
from tkinter import messagebox
import tkinter as tk


def prompt_for_credentials(passphrase: str) -> Optional[Credentials]:
    """
    GUI to prompt the user for subdomain and bearer token.
    Returns a Credentials object based on the user's input.
    """
    result = None

    def submit_credentials(event=None):
        nonlocal result
        subdomain = subdomain_entry.get().strip()
        bearer_token = token_entry.get().strip()

        if not subdomain or not bearer_token:
            messagebox.showerror(
                "Error", "Both subdomain and token are required!")
            return

        try:
            result = Credentials(subdomain, bearer_token)
            root.destroy()
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))

    def cancel_credentials():
        nonlocal result
        result = None
        root.destroy()

    def toggle_passphrase_visibility():
        if passphrase_entry.cget("show") == "*":
            passphrase_entry.config(show="")
            toggle_button.config(text="Hide")
        else:
            passphrase_entry.config(show="*")
            toggle_button.config(text="Show")

    # GUI setup
    root = tk.Tk()
    root.title("Enter Credentials")
    root.attributes('-topmost', True)
    result = None

    # Passphrase label and entry (hidden initially)
    tk.Label(root, text="Key used for hashing:").pack(pady=5)
    passphrase_entry = tk.Entry(root, show="*")
    passphrase_entry.insert(0, passphrase)
    passphrase_entry.pack(pady=5)

    # Toggle button to show/hide passphrase
    toggle_button = tk.Button(
        root, text="Show", command=toggle_passphrase_visibility)
    toggle_button.pack(pady=5)

    # Subdomain label and entry
    tk.Label(root, text="Enter your YouTrack subdomain (e.g., 'brunata')").pack(
        pady=5)
    subdomain_entry = tk.Entry(root)
    subdomain_entry.pack(pady=5)
    subdomain_entry.focus_set()

    # Bearer token label and entry (bearer token hidden initially)
    tk.Label(root, text="Enter your YouTrack permanent token").pack(pady=5)
    token_entry = tk.Entry(root, show="*")  # Hide the token input for security
    token_entry.pack(pady=5)

    # Buttons to submit or cancel
    tk.Button(root, text="OK", command=submit_credentials).pack(
        side="left", padx=10, pady=10)
    tk.Button(root, text="Cancel", command=cancel_credentials).pack(
        side="right", padx=10, pady=10)

    # Bind Enter key to submit action
    root.bind('<Return>', submit_credentials)
    root.mainloop()

    return result
