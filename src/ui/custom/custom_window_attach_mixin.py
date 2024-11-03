from typing import Literal
from pydantic import BaseModel
from ui.custom.custom_toplevel import CustomTopLevel
import tkinter as tk


class AttachedCustomTopLevel(BaseModel):
    top_level: CustomTopLevel
    position: Literal["left", "right", "top", "bottom"]

    class Config:
        arbitrary_types_allowed = True


class CustomWindowAttachMixin:
    """Mixin that it possible to attach any Tkinter window to the left, top, right or bottom of other Tkinter windows."""

    def __init__(self):
        super().__init__()
        self._attached_top_levels: list[AttachedCustomTopLevel] = []

    def attach_windows(self, attached_top_levels: list[tuple[CustomTopLevel, Literal["left", "right", "top", "bottom"]]]):
        """
        Attach multiple windows with specified positions.
        Accepts a list of (CustomTopLevel, position) tuples.
        """
        for top_level, position in attached_top_levels:
            attached_top_level = AttachedCustomTopLevel(
                top_level=top_level, position=position)
            self._attached_top_levels.append(attached_top_level)

    def _get_cumulative_offset(self, attached_top_level: AttachedCustomTopLevel) -> int:
        """Calculate cumulative offset for windows attached in the same position."""
        same_position_windows = [
            atl for atl in self._attached_top_levels if atl.position == attached_top_level.position]
        index = same_position_windows.index(attached_top_level)
        offset = 0
        for i in range(index):
            other_window = same_position_windows[i].top_level.get_window()
            other_window.update_idletasks()
            if attached_top_level.position in ["top", "bottom"]:
                offset += other_window.winfo_width()
            elif attached_top_level.position in ["left", "right"]:
                offset += other_window.winfo_height()
        return offset

    def _update_position(self, attached_top_level: AttachedCustomTopLevel):
        """Calculate and apply the position based on the parent window."""
        window = attached_top_level.top_level.get_window()
        if window is None:
            return

        window.update_idletasks()
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        title_bar_height = self.winfo_rooty() - self.winfo_y()

        window_width = window.winfo_width()
        window_height = window.winfo_height()

        # Adjust the offset based on the cumulative position for the current window
        cumulative_offset = self._get_cumulative_offset(attached_top_level)

        position = attached_top_level.position
        if position == "right":
            new_x = parent_x + parent_width
            new_y = parent_y + cumulative_offset
        elif position == "left":
            new_x = parent_x - window_width
            new_y = parent_y + cumulative_offset
        elif position == "top":
            new_x = parent_x + cumulative_offset
            new_y = parent_y - window_height - title_bar_height
        elif position == "bottom":
            new_x = parent_x + cumulative_offset
            new_y = parent_y + parent_height + title_bar_height

        window.geometry(f"+{new_x}+{new_y}")

    def _bind_update_position(self, attached_top_level: AttachedCustomTopLevel):
        """Bind the update position function for a specific attached top level."""
        self.bind("<Configure>", lambda event,
                  atl=attached_top_level: self._update_position(atl), add='+')

    def show_all_attached_windows(self, parent_window: tk.Tk):
        """Show and position all attached windows."""
        for attached_top_level in self._attached_top_levels:
            attached_top_level.top_level.show(parent_window)
            self._bind_update_position(attached_top_level)

    def hide_all_attached_windows(self):
        """Hide all attached windows."""
        for attached_top_level in self._attached_top_levels:
            attached_top_level.top_level.hide()

    def destroy_all_attached_windows(self):
        """Destroy all attached windows and clear the list."""
        for attached_top_level in self._attached_top_levels:
            attached_top_level.top_level.destroy()
        self._attached_top_levels.clear()
