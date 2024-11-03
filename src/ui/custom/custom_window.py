import logging
import tkinter as tk
from typing import Optional

from errors.user_cancelled_error import UserCancelledError
from ui.custom.custom_window_config import CustomWindowConfig
from ui.custom.custom_window_attach_mixin import CustomWindowAttachMixin

logger = logging.getLogger(__name__)


class CustomWindow(tk.Tk, CustomWindowAttachMixin):
    def __init__(self, config: Optional[CustomWindowConfig] = None) -> tk.Tk:
        super().__init__()
        CustomWindowAttachMixin.__init__(self)

        self.__cancelled = True
        self.config = config if config is not None else CustomWindowConfig()
        self.title(self.config.title)
        self.attributes('-topmost', self.config.topmost)

        self.config.cancel_key and self.bind(
            f"<{self.config.cancel_key}>", self._destroy)
        self.config.submit_key and self.bind(
            f"<{self.config.submit_key}>", self._submit)

        self._set_window_geometry()

        self.resizable(self.config.resizable, self.config.resizable)

    def show(self):
        self.show_all_attached_windows()
        self.mainloop()

        if self.__cancelled:
            raise UserCancelledError()

    def _set_window_geometry(self):
        """Set window size and position in the center of the screen."""
        width = self.config.width
        height = self.config.height
        pos_right = int(self.winfo_screenwidth() / 2 - width / 2)
        pos_down = int(self.winfo_screenheight() / 2 - height / 2)
        self.geometry(f"{width}x{height}+{pos_right}+{pos_down}")

    def _destroy(self, event=None):
        self.destroy()

    def _submit(self, event=None):
        self.__cancelled = False
        self.destroy()
