import logging
import tkinter as tk
from typing import Optional

from errors.user_cancelled_error import UserCancelledError
from ui.custom.custom_window_config import CustomWindowConfig
from ui.custom.window_attach_mixin import WindowAttachMixin

logger = logging.getLogger(__name__)


class CustomWindow(tk.Tk, WindowAttachMixin):
    def __init__(self, config: Optional[CustomWindowConfig] = None) -> tk.Tk:
        super().__init__()
        WindowAttachMixin.__init__(self)

        self.__cancelled = True
        self.config = config if config is not None else CustomWindowConfig()
        self.title(self.config.title)
        self.attributes('-topmost', self.config.topmost)

        self.on_destroy = config.destroy_action.action
        self.on_submit = config.submit_action.action
        self.config.destroy_action.key and self.bind(
            f"<{self.config.destroy_action.key}>", self._destroy_on_action)
        self.config.submit_action.key and self.bind(
            f"<{self.config.submit_action.key}>", self._submit_on_action)

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

    def _destroy_on_action(self, event=None):
        if self.config.destroy_action is None:
            return
        if self.on_destroy is not None:
            self.on_destroy()
            return
        self.destroy()

    def _submit_on_action(self, event=None):
        self.__cancelled = False
        if self.config.submit_action is None:
            return
        if self.on_submit is not None:
            self.on_submit()
        self.destroy()
