import tkinter as tk
from tkinter import messagebox
from typing import Optional


def display_bearer_token_prompt() -> Optional[str]:
    """
    GUI to prompt the user for a YouTrack bearer token.
    Returns the token as a string based on the user's input.
    """
    token = None

    def submit_token(event=None):
        nonlocal token
        entered_token = token_entry.get().strip()

        if not entered_token:
            messagebox.showerror("Error", "Token is required!")
            return

        token = entered_token
        root.destroy()

    def cancel_token():
        nonlocal token
        token = None
        root.destroy()

    # GUI setup
    root = tk.Tk()
    root.title("Enter Token")
    root.attributes('-topmost', True)

    # Bearer token label and entry (bearer token hidden initially)
    tk.Label(root, text="Enter your YouTrack permanent token").pack(pady=5)
    token_entry = tk.Entry(root, show="*")  # Hide the token input for security
    token_entry.pack(pady=5)
    token_entry.focus_set()

    # Buttons to submit or cancel
    tk.Button(root, text="OK", command=submit_token).pack(
        side="left", padx=10, pady=10)
    tk.Button(root, text="Cancel", command=cancel_token).pack(
        side="right", padx=10, pady=10)

    # Bind Enter key to submit action
    root.bind('<Return>', submit_token)
    root.mainloop()

    return token
