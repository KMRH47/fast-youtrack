import platform
import subprocess
import tkinter as tk
from typing import Any, Callable, List, Optional, Tuple

from ui.views.base.custom_view import CustomView
from ui.constants.tk_events import TkEvents


def _get_extents_title_bar_height(window_id: int) -> Optional[int]:
    try:
        result = subprocess.run(
            ["xprop", "-id", str(window_id), "_NET_FRAME_EXTENTS"],
            capture_output=True,
            text=True,
            timeout=1,
        )
        if result.returncode != 0 or "_NET_FRAME_EXTENTS" not in result.stdout:
            return None
        extents = result.stdout.split("=")[1].strip().split(",")
        if len(extents) < 3:
            return None
        top_extent = int(extents[2].strip())
        return top_extent if top_extent > 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return None


def _guess_desktop_title_bar_height() -> Optional[int]:
    try:
        desktop = subprocess.run(
            ["echo", "$XDG_CURRENT_DESKTOP"], capture_output=True, text=True, shell=True
        )
        desktops = {
            "cinnamon": 32,
            "gnome": 38,
            "kde": 30,
        }
        desktop_str = desktop.stdout.lower()
        for name, height in desktops.items():
            if name in desktop_str:
                return height
    except Exception:
        pass
    return None


class CustomWindowAttachMixin(tk.Tk):
    """Mixin that it possible to attach any Tkinter window to the left, top, right or bottom of other Tkinter views."""

    def __init__(
        self,
        attached_views: Optional[List[Callable[[], CustomView]]] = None,
    ):
        super().__init__()
        self.__attached_views: List[CustomView] = (
            [factory() for factory in attached_views] if attached_views else []
        )

    def attach_views(self, custom_views: List[CustomView]) -> None:
        """
        Attach multiple views with specified positions.
        Accepts a list of (CustomTopLevel, position) tuples.
        """
        self.__attached_views = custom_views

    def get_attached_views(self) -> List[CustomView]:
        """Return a list of attached top-level views."""
        return self.__attached_views

    def show_all_attached_views(self) -> None:
        """Show and position all attached views."""
        for attached_view in self.__attached_views:
            self._bind_update_position(attached_view)
            attached_view._show(self)  # pyright: ignore[reportPrivateUsage]

    def hide_all_attached_views(self) -> None:
        """Hide all attached views."""
        for attached_view in self.__attached_views:
            attached_view._hide()  # pyright: ignore[reportPrivateUsage]

    def destroy_all_attached_views(self) -> None:
        """Destroy all attached views and clear the list."""
        for attached_view in self.__attached_views:
            attached_view.destroy()
        self.__attached_views.clear()

    def _get_cumulative_offset(self, attached_view: CustomView) -> int:
        position = attached_view._get_position()  # pyright: ignore[reportPrivateUsage]
        same_position_views = [
            view
            for view in self.__attached_views
            if view._get_position() == position  # pyright: ignore[reportPrivateUsage]
        ]
        view_index = same_position_views.index(attached_view)
        is_horizontal = position in {"top", "bottom"}

        def get_dimension(view: CustomView) -> int:
            view.update_idletasks()
            return view.winfo_width() if is_horizontal else view.winfo_height()

        return sum(get_dimension(view) for view in same_position_views[:view_index])

    def _calculate_title_bar_height(self) -> int:
        try:
            window_y = self.winfo_rooty()
            client_y = self.winfo_y()
            delta = window_y - client_y
            if delta > 0:
                return delta

            extents = _get_extents_title_bar_height(self.winfo_id())
            if extents:
                return extents

            desktop_guess = _guess_desktop_title_bar_height()
            if desktop_guess:
                return desktop_guess

        except Exception:
            pass
        return 35

    def _parent_geometry(self) -> Tuple[int, int, int, int]:
        """Return (x, y, width, height) of parent."""
        return (
            self.winfo_rootx(),
            self.winfo_rooty(),
            self.winfo_width(),
            self.winfo_height(),
        )

    def _title_bar_correction(self) -> int:
        if platform.system() != "Linux":
            return 0
        return self._calculate_title_bar_height()

    def _content_area_y(self, parent_y: int) -> int:
        return parent_y + self._title_bar_correction()

    def _position_offset(self, attached_view: CustomView) -> int:
        return self._get_cumulative_offset(attached_view)

    def _calculate_coordinates(
        self,
        attached_view: CustomView,
        parent_geom: Tuple[int, int, int, int],
        content_area_y: int,
        offset: int,
        title_bar_height: int,
    ) -> Tuple[int, int]:
        parent_x, parent_y, parent_w, parent_h = parent_geom
        win_w = attached_view.winfo_width()
        win_h = attached_view.winfo_height()
        pos = attached_view._get_position()  # pyright: ignore[reportPrivateUsage]

        if pos == "right":
            return parent_x + parent_w, content_area_y + offset

        if pos == "left":
            return parent_x - win_w, content_area_y + offset

        if pos == "top":
            new_x = parent_x + offset
            new_y = (
                parent_y - win_h - title_bar_height
                if platform.system() == "Linux"
                else self.winfo_y() - win_h
            )
            return new_x, new_y

        if pos == "bottom":
            return parent_x + offset, parent_y + parent_h

        raise ValueError(f"Unknown position: {pos}")

    def _update_position(self, attached_view: CustomView) -> None:
        parent_geom = self._parent_geometry()
        title_bar_height = self._title_bar_correction()
        content_area_y = self._content_area_y(parent_geom[1])
        offset = self._position_offset(attached_view)
        x, y = self._calculate_coordinates(
            attached_view, parent_geom, content_area_y, offset, title_bar_height
        )
        attached_view.geometry(f"+{x}+{y}")

    def _bind_update_position(self, attached_view: CustomView) -> None:
        """Bind the update position function for a specific attached top level."""
        self.bind(
            TkEvents.GEOMETRY_CHANGED,
            lambda event, attached_view_arg=attached_view: self._update_position(
                attached_view_arg
            ),
            add="+",
        )

    def _on_minimize(self, event: Optional[Any] = None) -> None:
        for attached_view in self.__attached_views:
            attached_view.withdraw()

    def _on_restore(self, event: Optional[Any] = None) -> None:
        for attached_view in self.__attached_views:
            attached_view.deiconify()
