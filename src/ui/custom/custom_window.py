import logging
import tkinter as tk
from typing import Callable, Optional

from errors.user_cancelled_error import UserCancelledError
from ui.custom.custom_view import CustomView
from ui.custom.custom_view_config import CustomViewConfig
from ui.custom.custom_window_attach_mixin import CustomWindowAttachMixin

logger = logging.getLogger(__name__)


class CustomWindow(CustomWindowAttachMixin):
    def __init__(
        self,
        attached_views: Optional[list[Callable[[], CustomView]]] = None,
        config: Optional[CustomViewConfig] = CustomViewConfig(),
    ) -> tk.Tk:
        super().__init__(attached_views=attached_views)
        self._config = config
        self.__cancelled = True
        
        self.title(self._config.title)
        self.attributes("-topmost", self._config.topmost)

        self._config.cancel_key and self.bind(
            f"<{self._config.cancel_key}>", self._destroy
        )
        self._config.submit_key and self.bind(
            f"<{self._config.submit_key}>", self._submit
        )

        self._set_window_geometry()

        self.resizable(self._config.resizable, self._config.resizable)

    def show(self):
        self.deiconify()
        self.update_idletasks()
        self.show_all_attached_views()
        self.mainloop()

        if self.__cancelled:
            raise UserCancelledError()

    def _set_window_geometry(self):
        """Set window size and position in the center of the screen."""
        width = self._config.width
        height = self._config.height
        pos_right = int(self.winfo_screenwidth() / 2 - width / 2)
        pos_down = int(self.winfo_screenheight() / 2 - height / 2)
        self.geometry(f"{width}x{height}+{pos_right}+{pos_down}")

    def _destroy(self, event=None):
        self.destroy()

    def _submit(self, event=None):
        self.__cancelled = False
        self.destroy()

    def _emit_value(self, value):
        return value
