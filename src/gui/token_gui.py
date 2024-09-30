import tkinter as tk
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
            display_error_dialog("Token is required!")
            return
        token = entered_token
        root.destroy()

    def cancel_token():
        nonlocal token
        token = None
        root.destroy()

    def display_error_dialog(message: str) -> None:
        error_window = tk.Toplevel(root)
        error_window.title("Error")
        error_window.attributes('-topmost', True)

        label = tk.Label(error_window, text=message, font=("Arial", 16))
        label.pack(padx=20, pady=20)

        close_button = tk.Button(error_window, text="OK",
                                 command=error_window.destroy)
        close_button.pack(pady=10)

        error_window.update_idletasks()
        window_width = error_window.winfo_width()
        window_height = error_window.winfo_height()
        position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
        error_window.geometry(f"+{position_right}+{position_down}")

        def ensure_focus():
            if not close_button.focus_get():
                close_button.focus_set()
                error_window.after(100, ensure_focus)

        error_window.after(1, ensure_focus)
        error_window.bind('<Return>', lambda event: error_window.destroy())

    root = tk.Tk()
    root.title("Enter Token")
    root.attributes('-topmost', True)

    root.update_idletasks()
    window_width = 300
    window_height = 150
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry(
        f"{window_width}x{window_height}+{position_right}+{position_down}")

    tk.Label(root, text="Enter your YouTrack permanent token",
             font=("Arial", 12)).pack(pady=10)
    token_entry = tk.Entry(root, show="*", font=("Arial", 10), width=30)
    token_entry.pack(pady=5)
    token_entry.focus_set()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    ok_button = tk.Button(button_frame, text="OK",
                          command=submit_token, width=10)
    ok_button.pack(side="left", padx=5)

    cancel_button = tk.Button(
        button_frame, text="Cancel", command=cancel_token, width=10)
    cancel_button.pack(side="left", padx=5)

    root.bind('<Return>', submit_token)

    root.mainloop()
    return token
