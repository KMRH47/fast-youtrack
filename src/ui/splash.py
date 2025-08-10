import tkinter as tk
from typing import Optional, Callable


class Splash:
    def __init__(self, message: str = "Starting Fast YouTrack..."):
        self._root: Optional[tk.Tk] = None
        self._message = message

    def show(self) -> None:
        if self._root is not None:
            return
        root = tk.Tk()
        root.title("Fast YouTrack")
        root.geometry("300x100")
        root.configure(bg="#2E8B57")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (300 // 2)
        y = (root.winfo_screenheight() // 2) - (100 // 2)
        root.geometry(f"+{x}+{y}")

        label = tk.Label(
            root,
            text=self._message,
            bg="#2E8B57",
            fg="#E0FFE0",
            font=("Arial", 13, "bold"),
        )
        label.pack(expand=True)
        self._root = root

        # do not block here; caller decides mainloop strategy
        root.update()

    def close(self) -> None:
        if self._root is None:
            return
        try:
            self._root.destroy()
        finally:
            self._root = None


