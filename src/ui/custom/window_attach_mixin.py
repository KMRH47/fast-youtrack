import tkinter as tk
from typing import Literal

class WindowAttachMixin:
    """Mixin that provides attach_window functionality for any Tkinter window."""
    def attach_window(self, window: tk.Toplevel, position: Literal["left", "right", "top", "bottom"] = "right", offset: int = 10):
        """Attaches the given window to the current window."""
        def update_position(event=None):
            parent_x = self.winfo_x()
            parent_y = self.winfo_y()
            parent_width = self.winfo_width()
            parent_height = self.winfo_height()

            title_bar_height = self.winfo_rooty() - self.winfo_y()

            if position == "right":
                new_x = parent_x + parent_width + offset
                new_y = parent_y
            elif position == "left":
                new_x = parent_x - window.winfo_width() - offset
                new_y = parent_y
            elif position == "top":
                new_x = parent_x
                new_y = parent_y - window.winfo_height() - offset - title_bar_height
            elif position == "bottom":
                new_x = parent_x
                new_y = parent_y + parent_height + offset + title_bar_height

            window.geometry(f"+{new_x}+{new_y}")

        # Bind the window movement to the parent window's movement
        self.bind("<Configure>", update_position)

        # Set the initial position
        update_position()
