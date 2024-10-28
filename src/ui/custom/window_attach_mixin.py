import logging
from typing import Literal
from ui.custom.custom_toplevel import CustomTopLevel

logger = logging.getLogger(__name__)


class WindowAttachMixin:
    """Mixin that provides attach_window functionality for any Tkinter window."""

    def attach_window(self, top_level: CustomTopLevel | None, position: Literal["left", "right", "top", "bottom"] = "right", offset: int = 10):
        if top_level is None:
            return

        # Show the window to initialize it
        top_level.show()
        window = top_level.get_window()

        # Ensure all updates are applied
        window.update_idletasks()

        # Function to calculate and apply the new position
        def update_position(event=None):
            parent_x = self.winfo_x()
            parent_y = self.winfo_y()
            parent_width = self.winfo_width()
            parent_height = self.winfo_height()
            window_width = window.winfo_width()
            window_height = window.winfo_height()

            title_bar_height = self.winfo_rooty() - self.winfo_y()

            # Calculate new_x and new_y based on the specified position
            if position == "right":
                new_x = parent_x + parent_width + offset
                new_y = parent_y
            elif position == "left":
                new_x = parent_x - window_width - offset
                new_y = parent_y
            elif position == "top":
                new_x = parent_x
                new_y = parent_y - window_height - offset - title_bar_height
            elif position == "bottom":
                new_x = parent_x
                new_y = parent_y + parent_height + offset + title_bar_height

            # Set position
            window.geometry(f"+{new_x}+{new_y}")

        # Bind the update_position function to <Configure> to follow main window movements
        self.bind("<Configure>", update_position, add='+')

        # Initial position setup
        update_position()
