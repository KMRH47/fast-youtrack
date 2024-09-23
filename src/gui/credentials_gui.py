import logging
import tkinter as tk
from tkinter import messagebox
from typing import Tuple


class ToolTip:
    """
    Class for creating tooltips that appear on hover.
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, _):
        if self.tooltip_window or not self.text:
            return
        # Get widget coordinates and size
        x, y, width, height = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + width // 2
        y += self.widget.winfo_rooty() + height // 2

        # Create a top-level window for the tooltip
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window borders
        tw.geometry(f"+{x+20}+{y+20}")  # Set the tooltip location

        # Create and display the tooltip label
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffff", relief='solid', borderwidth=1,
                         font=("tahoma", "10", "normal"))
        label.pack(ipadx=1, ipady=1)

    def hide_tooltip(self, _):
        if self.tooltip_window:
            self.tooltip_window.destroy()  # Destroy the tooltip window
            self.tooltip_window = None


def prompt_for_credentials(passphrase: str) -> Tuple[str, str]:
    """
    GUI to prompt the user for subdomain and bearer token.
    Returns the subdomain and bearer_token as a tuple.
    """
    def submit_credentials(event=None):
        nonlocal result
        subdomain = subdomain_entry.get()
        bearer_token = token_entry.get()

        if not subdomain or not bearer_token:
            messagebox.showerror(
                "Error", "Both subdomain and token are required!")
            return

        result = (subdomain, bearer_token)
        root.destroy()

    def cancel_credentials():
        nonlocal result
        result = None
        root.destroy()

    # GUI setup
    root = tk.Tk()
    root.title("Enter Credentials")
    root.attributes('-topmost', True)
    result = None

    tk.Label(root, text=f"Key used for hashing: {passphrase}").pack(pady=5)
    tk.Label(root, text="Enter your YouTrack subdomain (e.g., 'brunata')").pack(
        pady=5)
    subdomain_entry = tk.Entry(root)
    subdomain_entry.pack(pady=5)
    subdomain_entry.focus_set()

    tk.Label(root, text="Enter your YouTrack permanent token").pack(pady=5)
    token_entry = tk.Entry(root, show="*")  # Hide the token input for security
    token_entry.pack(pady=5)

    tk.Button(root, text="OK", command=submit_credentials).pack(
        side="left", padx=10, pady=10)
    tk.Button(root, text="Cancel", command=cancel_credentials).pack(
        side="right", padx=10, pady=10)

    root.bind('<Return>', submit_credentials)
    root.mainloop()

    return result
