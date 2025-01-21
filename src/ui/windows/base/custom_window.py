import logging

from typing import Optional, Callable
import tkinter as tk

from errors.user_cancelled_error import UserCancelledError
from ui.constants.tk_events import TkEvents
from ui.views.base.custom_window_config import CustomWindowConfig
from ui.windows.base.custom_window_attach_mixin import CustomWindowAttachMixin
from errors.user_error import UserError


logger = logging.getLogger(__name__)


class CustomWindow(CustomWindowAttachMixin):
    def __init__(
        self,
        config: Optional[CustomWindowConfig] = CustomWindowConfig(),
        **kwargs,
    ):
        attached_views = kwargs.pop("attached_views", None)
        super().__init__(attached_views=attached_views)
        self.withdraw()  # hide window initially to avoid flickering
        self._config = config
        self.__cancelled = True
        self.__submit_callback = None

        self.title(self._config.title)

        self.bind(TkEvents.WINDOW_UNMAPPED, self._on_minimize)
        self.bind(TkEvents.WINDOW_MAPPED, self._on_restore)

        if self._config.bg_color:
            self.option_add("*Background", self._config.bg_color)
        if self._config.text_color:
            self.option_add("*Foreground", self._config.text_color)

        self.attributes("-topmost", self._config.topmost)
        self.configure(bg=self._config.bg_color)

        self._config.cancel_key and self.bind(
            f"<{self._config.cancel_key}>", self._on_window_close
        )
        self._config.submit_key and self.bind(
            f"<{self._config.submit_key}>", self._submit
        )

        self._set_window_geometry()
        self.resizable(self._config.resizable, self._config.resizable)

    def show(self):
        self.show_all_attached_views()
        self.update_idletasks()
        self.deiconify()
        self.focus_force()

        if not hasattr(self, '_mainloop_running'):
            self._mainloop_running = True
            self.mainloop()

        if self.__cancelled:
            raise UserCancelledError()

    def bind_submit(self, handler: Callable) -> None:
        self.__submit_callback = handler

    def report_callback_exception(self, exc, val, tb):
        """Override Tkinter's error handling function"""

        # display error dialog on UserError
        if isinstance(val, UserError):
            val.display()

    def _set_window_geometry(self):
        """Set window size and position in the center of the screen."""
        width = self._config.width
        height = self._config.height
        pos_right = int(self.winfo_screenwidth() / 2 - width / 2)
        pos_down = int(self.winfo_screenheight() / 2 - height / 2)
        self.geometry(f"{width}x{height}+{pos_right}+{pos_down}")

    def _destroy(self, _):
        self.destroy()

    def _submit(self, _):
        if self.__submit_callback:
            self.__submit_callback()
        self.__cancelled = False
        self._on_window_close()

    def _emit_value(self, value):
        return value

    def _on_window_close(self, event=None):
        self.hide_all_attached_views()
        self.iconify()
