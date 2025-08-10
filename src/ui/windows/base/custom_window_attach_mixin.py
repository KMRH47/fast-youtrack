import platform
import subprocess
import tkinter as tk
from typing import Any, Callable, List, Optional, Tuple

from ui.views.base.custom_view import CustomView
from ui.constants.tk_events import TkEvents


class CustomWindowAttachMixin(tk.Tk):

    def __init__(
        self,
        attached_views: Optional[List[Callable[[], CustomView]]] = None,
    ):
        super().__init__()
        self.__attached_views: List[CustomView] = (
            [factory() for factory in attached_views] if attached_views else []
        )

    def _nswindow_for(self, win: tk.Misc):
        """Get the NSWindow for a Tk window on macOS."""
        win.update_idletasks()
        from AppKit import NSApp, NSApplication

        app = NSApp() or NSApplication.sharedApplication()
        token, old = f"__tk_{id(win)}__", win.wm_title()
        win.wm_title(token)
        win.update_idletasks()
        try:
            for w in app.windows():
                if str(getattr(w, "title", lambda: "")()) == token:
                    return w
        finally:
            win.wm_title(old)
        raise RuntimeError("NSWindow not found for Tk window")

    def _attach_child_window(self, child: tk.Misc, parent: tk.Misc):
        """Attach child window as native Cocoa child of parent."""
        from AppKit import NSWindowAbove

        p = self._nswindow_for(parent)
        c = self._nswindow_for(child)
        p.addChildWindow_ordered_(c, NSWindowAbove)

    def _detach_child_window(self, child: tk.Misc, parent: tk.Misc):
        """Detach child window from parent."""
        p = self._nswindow_for(parent)
        c = self._nswindow_for(child)
        p.removeChildWindow_(c)

    def _get_extents_title_bar_height(self, window_id: int) -> Optional[int]:
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

    def _guess_desktop_title_bar_height(self) -> Optional[int]:
        try:
            desktop = subprocess.run(
                ["echo", "$XDG_CURRENT_DESKTOP"],
                capture_output=True,
                text=True,
                shell=True,
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

    def _macos_title_bar_height(self, window: tk.Tk) -> Optional[int]:
        try:
            probe = tk.Frame(window, width=1, height=1)
            probe.place(x=0, y=0)
            window.update_idletasks()
            offset = probe.winfo_rooty() - window.winfo_rooty()
            probe.destroy()
            return int(offset) if offset and offset > 0 else None
        except Exception:
            return None

    def attach_views(self, custom_views: List[CustomView]) -> None:
        self.__attached_views = custom_views

    def get_attached_views(self) -> List[CustomView]:
        return self.__attached_views

    def show_all_attached_views(self) -> None:
        is_macos = platform.system() == "Darwin"
        for attached_view in self.__attached_views:
            attached_view._show(self)  # pyright: ignore[reportPrivateUsage]
            if is_macos:
                try:
                    self._update_position(attached_view)
                    self._attach_child_window(attached_view, self)
                except Exception as e:
                    print(f"Failed to attach child window: {e}")
                    self._bind_update_position(attached_view)
            else:
                self._bind_update_position(attached_view)
                try:
                    self.after(0, lambda v=attached_view: self._update_position(v))
                except Exception:
                    pass

    def hide_all_attached_views(self) -> None:
        for attached_view in self.__attached_views:
            if platform.system() == "Darwin":
                try:
                    self._detach_child_window(attached_view, self)
                except Exception:
                    pass
            attached_view._hide()  # pyright: ignore[reportPrivateUsage]

    def destroy_all_attached_views(self) -> None:
        for attached_view in self.__attached_views:
            if platform.system() == "Darwin":
                try:
                    self._detach_child_window(attached_view, self)
                except Exception:
                    pass
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
        if platform.system() == "Darwin":
            return 0

        try:
            self.update_idletasks()
            window_y = self.winfo_rooty()
            client_y = self.winfo_y()
            delta = window_y - client_y
            if delta > 0:
                return delta

            extents = self._get_extents_title_bar_height(self.winfo_id())
            if extents:
                return extents

            desktop_guess = self._guess_desktop_title_bar_height()
            if desktop_guess:
                return desktop_guess

        except Exception:
            pass

        if platform.system() == "Windows":
            return 30
        return 35

    def _parent_geometry(self) -> Tuple[int, int, int, int]:
        return (
            self.winfo_rootx(),
            self.winfo_rooty(),
            self.winfo_width(),
            self.winfo_height(),
        )

    def _title_bar_correction(self) -> int:
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
        try:
            attached_view.update_idletasks()
        except Exception:
            pass
        win_w = attached_view.winfo_width()
        win_h = attached_view.winfo_height()
        if win_w <= 1:
            try:
                win_w = int(getattr(attached_view, "_config").width)
            except Exception:
                pass
        if win_h <= 1:
            try:
                win_h = int(getattr(attached_view, "_config").height)
            except Exception:
                pass
        pos = attached_view._get_position()  # pyright: ignore[reportPrivateUsage]

        if pos == "right":
            return parent_x + parent_w, content_area_y + offset

        if pos == "left":
            return parent_x - win_w, content_area_y + offset

        if pos == "top":
            new_x = parent_x + offset
            if platform.system() == "Darwin":
                new_y = (self.winfo_y() - title_bar_height) - win_h
            elif platform.system() == "Linux":
                new_y = parent_y - win_h - title_bar_height
            else:
                new_y = parent_y - win_h
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
