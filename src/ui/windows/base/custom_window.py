import logging
import threading
from typing import Optional, Callable

from PIL import Image, ImageDraw
from pystray import Icon, MenuItem, Menu

from errors.user_cancelled_error import UserCancelledError
from ui.constants.tk_events import TkEvents
from ui.views.base.custom_window_config import CustomWindowConfig
from ui.windows.base.custom_window_attach_mixin import CustomWindowAttachMixin
from errors.user_error import UserError
from utils.pid_utils import cleanup_pids_folder

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
        self.tray_icon = None
        self.tray_thread = None

        self.title(self._config.title)

        self.bind(TkEvents.WINDOW_UNMAPPED, self._on_minimize)
        self.bind(TkEvents.WINDOW_MAPPED, self._on_restore)

        if self._config.bg_color:
            self.option_add("*Background", self._config.bg_color)
        if self._config.text_color:
            self.option_add("*Foreground", self._config.text_color)

        self.attributes("-topmost", self._config.topmost)
        self.attributes("-toolwindow", self._config.minimize_to_tray)
        self.configure(bg=self._config.bg_color)

        if self._config.cancel_key:
            self.bind(f"<{self._config.cancel_key}>", self._on_window_close)
        if self._config.submit_key:
            self.bind(f"<{self._config.submit_key}>", self._submit)

        self._set_window_geometry()
        self.resizable(self._config.resizable, self._config.resizable)

    def show(self):
        self.show_all_attached_views()
        self.update_idletasks()
        self.deiconify()
        self.lift()
        self.focus_force()

        if not hasattr(self, "_mainloop_running"):
            self._mainloop_running = True
            self.mainloop()

        if self.__cancelled:
            raise UserCancelledError()

    def bind_submit(self, handler: Callable) -> None:
        self.__submit_callback = handler

    def report_callback_exception(self, exc, val, tb):
        """Override Tkinter's error handling function"""
        if isinstance(val, UserError):
            val.display()

    def set_is_loading(self, is_loading: bool) -> None:
        for view in self.get_attached_views():
            view.set_is_loading(is_loading)

    def _set_window_geometry(self):
        width = self._config.width
        height = self._config.height
        pos_right = int(self.winfo_screenwidth() / 2 - width / 2)
        pos_down = int(self.winfo_screenheight() / 2 - height / 2)
        self.geometry(f"{width}x{height}+{pos_right}+{pos_down}")

    def _submit(self, _):
        if self.__submit_callback:
            self.__submit_callback()
        self.__cancelled = False
        self._on_window_close()

    def _emit_value(self, value):
        return value

    def _on_window_close(self, event=None):
        logger.debug("Minimizing to tray")
        self.withdraw()
        self._show_tray_icon()

    def _reset_attached_views(self):
        for view in self.get_attached_views():
            view._reset()

    def _restore_window(self, icon, item=None):
        """Restore window from system tray."""
        logger.debug("Restoring window from system tray")
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.deiconify()
        self.lift()
        self.focus_force()

    def _exit_app(self, icon, item):
        """Exit the application cleanly."""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

        cleanup_pids_folder()
        self.destroy()

    def _show_tray_icon(self):
        """Start the system tray icon in a separate thread."""
        if not self.tray_icon:
            self.tray_icon = self._create_tray_icon()

        if not self.tray_thread or not self.tray_thread.is_alive():
            logger.debug("Starting tray icon thread")
            self.tray_thread = threading.Thread(
                target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()

    def _create_tray_icon(self):
        """Create system tray icon with menu options."""
        icon_size = (64, 64)
        image = Image.new("RGB", icon_size, (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((10, 10, 54, 54), fill=(255, 0, 0))

        menu = Menu(
            MenuItem("Show", self._restore_window,
                     default=True, visible=False),
            MenuItem("Exit", self._exit_app),
        )

        return Icon(self._config.app_name, image, self._config.title, menu)
