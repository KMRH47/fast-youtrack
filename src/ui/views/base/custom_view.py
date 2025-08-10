import logging
import math
import platform
import tkinter as tk

from typing import Literal, Optional, TypeVar

from ui.views.base.custom_view_config import CustomViewConfig
from ui.constants.tk_events import TkEvents


logger = logging.getLogger(__name__)

T = TypeVar("T")


class CustomView(tk.Toplevel):
    def __init__(
        self,
        parent_window: Optional[tk.Tk] = None,
        config: CustomViewConfig = CustomViewConfig(),
    ):
        super().__init__(master=parent_window)
        self._config = config
        self._hide()  # hide view to avoid flickering
        self.__is_loading = False
        self.__loading_overlay = None

    def update_value(self, value: T) -> None:
        """Update the view with a new value.
        Note: This method is expected to be overridden by subclasses to use `value`.
        """
        pass

    def set_is_loading(self, is_loading: bool) -> None:
        if is_loading == self.__is_loading:
            return

        self.__is_loading = is_loading

        if is_loading:
            self._create_loading_overlay()
        else:
            self._destroy_loading_overlay()

    def get_is_loading(self) -> bool:
        return self.__is_loading

    def _show(self, parent_window: tk.Tk) -> None:
        self._create_view(parent_window)
        self._on_show()

    def _hide(self) -> None:
        self.withdraw()

    def _destroy(self) -> None:
        self.destroy()
        self = None

    def _create_view(self, parent_window: tk.Tk) -> None:
        self.master = parent_window
        self.geometry(f"{self._config.width}x{self._config.height}")

        if platform.system() == "Darwin":
            self._strip_titlebar()
        else:
            self.overrideredirect(True)

        self.wm_attributes("-topmost", self._config.topmost)
        self.resizable(self._config.resizable, self._config.resizable)
        self._build_ui()

    def _clear_view(self) -> None:
        """Destroy all child widgets of the given view."""
        for widget in self.winfo_children():
            widget.destroy()

    def _build_ui(self) -> None:
        """Build or rebuild the UI."""
        self._clear_view()

        container_frame = tk.Frame(self, padx=10, pady=10)
        container_frame.pack(fill="both", expand=True)
        self._populate_widgets(container_frame)

        self._disable_focus_for_all_widgets()

        self.update_idletasks()
        if isinstance(self.master, tk.Tk):
            self.master.event_generate(TkEvents.GEOMETRY_CHANGED)

    def _set_position(
        self, position: Literal["left", "right", "top", "bottom"]
    ) -> None:
        self._config.position = position

    def _get_position(self) -> Literal["left", "right", "top", "bottom"]:
        return self._config.position

    def _populate_widgets(self, parent: tk.Frame) -> None:
        pass

    def _on_show(self) -> None:
        pass

    def _reset(self) -> None:
        """Reset the view to its initial state."""
        pass

    def _disable_focus_for_all_widgets(self) -> None:
        """Recursively disable focus for all widgets in the view."""

        def disable_widget_focus(widget):
            try:
                if hasattr(widget, "config") and "takefocus" in widget.keys():
                    widget.config(takefocus=False)
            except Exception as e:
                logger.debug(f"Could not disable focus for widget {widget}: {e}")

            try:
                for child in widget.winfo_children():
                    disable_widget_focus(child)
            except Exception:
                pass

        disable_widget_focus(self)

    def _flash_update(
        self,
        flash_color: Literal["red", "green", "yellow"] = "yellow",
    ) -> None:
        """Flash the border with a smooth fade effect."""
        try:
            STEPS = 20
            DELAY = 8
            BORDER_WIDTH = 2
            FLASH_COLOR_MAP = {
                "red": "#FFCCCC",
                "green": "#CCFFCC",
                "yellow": "#FFFFCC",
            }

            target_color = FLASH_COLOR_MAP.get(flash_color, FLASH_COLOR_MAP["yellow"])
            bg_color = self._config.bg_color or self.cget("bg")

            if not bg_color.startswith("#"):
                rgb_tuple = self.winfo_rgb(bg_color)
                bg_color = f"#{rgb_tuple[0]//256:02x}{rgb_tuple[1]//256:02x}{rgb_tuple[2]//256:02x}"

            def interpolate(ratio: float) -> str:
                """Interpolate between background and target color."""
                try:
                    bg_rgb = [
                        int(bg_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
                    ]
                    target_rgb = [
                        int(target_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
                    ]
                    current_rgb = [
                        int(bg_rgb[i] + (target_rgb[i] - bg_rgb[i]) * ratio)
                        for i in range(3)
                    ]
                    return (
                        f"#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}"
                    )
                except Exception as e:
                    logging.error(f"Color interpolation failed: {e}")
                    return bg_color

            def fade_step(step: int = 0):
                if step > STEPS:
                    self.configure(
                        highlightthickness=BORDER_WIDTH,
                        highlightbackground=bg_color,
                    )
                    return

                ratio = math.sin((step / STEPS) * math.pi)
                color = interpolate(ratio)

                try:
                    self.configure(
                        highlightthickness=BORDER_WIDTH,
                        highlightbackground=color,
                    )
                except Exception as e:
                    logging.error(f"Widget update failed: {e}")
                    return

                self.after(DELAY, lambda: fade_step(step + 1))

            try:
                for after_id in self.tk.eval("after info").split():
                    self.after_cancel(int(after_id))
            except Exception:
                pass

            fade_step(0)

        except Exception as e:
            logging.error(f"Flash update failed: {e}")
            self.configure(
                highlightthickness=BORDER_WIDTH,
                highlightbackground=bg_color,
                highlightcolor=bg_color,
            )

    def _create_loading_overlay(self) -> None:
        """Create and show a loading overlay."""
        if self.__loading_overlay:
            return

        self.__loading_overlay = tk.Frame(
            self,
            bg=self._config.bg_color,
            borderwidth=0,
        )

        self.__loading_overlay.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1,
        )

        label = tk.Label(
            self.__loading_overlay,
            text="Loading...",
            font=("Segoe UI", 12, "bold"),
            bg=self._config.bg_color,
            fg=self._config.text_color,
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

        self.__loading_overlay.lift()

    def _destroy_loading_overlay(self) -> None:
        """Remove the loading overlay."""
        if self.__loading_overlay:
            self.__loading_overlay.destroy()
            self.__loading_overlay = None

    def _strip_titlebar(self):
        from AppKit import NSApp, NSApplication, NSWindowStyleMaskTitled

        self.update_idletasks()
        app = NSApp() or NSApplication.sharedApplication()
        token, old = f"__tk_{id(self)}__", self.wm_title()
        self.wm_title(token)
        self.update_idletasks()
        for w in app.windows():
            if str(w.title()) == token:
                w.setStyleMask_(w.styleMask() & ~NSWindowStyleMaskTitled)
                break
        self.wm_title(old)
