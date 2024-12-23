import tkinter as tk
from typing import Callable, Optional

from ui.custom.custom_view import CustomView


class CustomWindowAttachMixin(tk.Tk):
    """Mixin that it possible to attach any Tkinter window to the left, top, right or bottom of other Tkinter views."""

    __attached_views: list[CustomView]

    def __init__(
        self,
        attached_views: Optional[list[Callable[[], CustomView]]] = None,
    ):
        super().__init__()
        self.__attached_views = (
            [factory() for factory in attached_views] if attached_views else []
        )

    def attach_views(self, custom_views: list[CustomView]):
        """
        Attach multiple views with specified positions.
        Accepts a list of (CustomTopLevel, position) tuples.
        """
        self.__attached_views = custom_views

    def get_attached_views(self) -> list[CustomView]:
        """Return a list of attached top-level views."""
        return self.__attached_views

    def _get_cumulative_offset(self, attached_view: CustomView) -> int:
        """Calculate cumulative offset for views attached in the same position."""
        same_pos_views = [
            view for view in self.__attached_views
            if view._get_position() == attached_view._get_position()
        ]

        index = same_pos_views.index(attached_view)
        offset = 0
        for i in range(index):
            other_view = same_pos_views[i]
            other_view.update_idletasks()
            if attached_view._get_position() in ["top", "bottom"]:
                offset += other_view.winfo_width()
            elif attached_view._get_position() in ["left", "right"]:
                offset += other_view.winfo_height()
        return offset

    def _update_position(self, attached_view: CustomView):
        """Calculate and apply the position based on the parent window."""

        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        title_bar_height = self.winfo_rooty() - self.winfo_y()

        window_width = attached_view.winfo_width()
        window_height = attached_view.winfo_height()

        cumulative_offset = self._get_cumulative_offset(attached_view)

        position = attached_view._get_position()
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

        attached_view.geometry(f"+{new_x}+{new_y}")

    def _bind_update_position(self, attached_view: CustomView):
        """Bind the update position function for a specific attached top level."""
        self.bind(
            "<Configure>",
            lambda event, attached_view_arg=attached_view: self._update_position(
                attached_view_arg
            ),
            add="+",
        )

    def show_all_attached_views(self):
        """Show and position all attached views."""
        for attached_view in self.__attached_views:
            self._bind_update_position(attached_view)
            attached_view._show(self)

    def hide_all_attached_views(self):
        """Hide all attached views."""
        for attached_view in self.__attached_views:
            attached_view._hide()

    def destroy_all_attached_views(self):
        """Destroy all attached views and clear the list."""
        for attached_view in self.__attached_views:
            attached_view.destroy()
        self.__attached_views.clear()
