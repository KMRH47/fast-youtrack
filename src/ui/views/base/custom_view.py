import logging
import math
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
        self._hide()  # Hide view to avoid flickering

    def update_value(self, value: T) -> None:
        """Update the view with a new value.
        Note: This method is expected to be overridden by subclasses to use `value`.
        """
        pass

    def _show(self, parent_window: tk.Tk) -> None:
        self._create_view(parent_window)
        self.after(0, self.deiconify)
        self.update_idletasks()
        self._on_show()

    def _hide(self) -> None:
        self.withdraw()

    def _destroy(self) -> None:
        self.destroy()
        self = None

    def _create_view(self, parent_window: tk.Tk) -> None:
        self.master = parent_window

        geometry = f"{self._config.width}x{self._config.height}"
        self.geometry(geometry)
        self.overrideredirect(True)  # hides title bar
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

        self.update_idletasks()
        if isinstance(self.master, tk.Tk):
            # Notify parent window that geometry has changed to trigger repositioning
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
            bg_color = self._config.bg_color or self.cget(
                "bg"
            )  # Use default Tkinter bg

            # Convert system color name to hex if necessary
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
