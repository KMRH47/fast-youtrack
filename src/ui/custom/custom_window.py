import tkinter as tk
from typing import Optional, Callable, Literal

from ui.custom.window_attach_mixin import WindowAttachMixin


class CustomWindowConfig:
    """Configuration object for CustomWindow."""

    def __init__(self, width: int = 500, height: int = 500, resizable: bool = False,
                 title: str = "Untitled Window", topmost: bool = True, close_on_cancel: bool = True):
        self.width = width
        self.height = height
        self.resizable = resizable
        self.title = title
        self.topmost = topmost
        self.close_on_cancel = close_on_cancel


class CustomWindow(tk.Tk, WindowAttachMixin):
    def __init__(self, config: Optional[CustomWindowConfig] = None,
                 on_cancel: Optional[Callable] = None):
        super().__init__()

        self.config = config if config is not None else CustomWindowConfig()

        self.on_cancel_callback = on_cancel

        self.title(self.config.title)
        self.attributes('-topmost', self.config.topmost)

        self.bind("<Escape>", self._on_cancel)

        self._set_window_geometry()

        self.resizable(self.config.resizable, self.config.resizable)

    def _set_window_geometry(self):
        """Set window size and position in the center of the screen."""
        width = self.config.width
        height = self.config.height
        pos_right = int(self.winfo_screenwidth() / 2 - width / 2)
        pos_down = int(self.winfo_screenheight() / 2 - height / 2)
        self.geometry(f"{width}x{height}+{pos_right}+{pos_down}")

    def _on_cancel(self, event=None):
        if not self.config.close_on_cancel:
            return
        self.destroy()
