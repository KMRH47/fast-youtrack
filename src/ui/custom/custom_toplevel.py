import functools
import logging
import tkinter as tk
from typing import Optional, Any
from abc import ABC, abstractmethod

from ui.custom.custom_window_config import CustomWindowConfig

logger = logging.getLogger(__name__)


class CustomTopLevel(ABC):
    def __init__(self, config: CustomWindowConfig = CustomWindowConfig()):
        self._config = config
        self._window: Optional[tk.Toplevel] = None
        self._update_job: Optional[str] = None

    def show(self, parent_window: tk.Tk) -> None:
        self._create_window(parent_window)
        self._window.transient(parent_window)
        self._window.deiconify()
        self._window.update_idletasks()
        self._on_show()

    def _create_window(self, parent_window: tk.Tk) -> None:
        self._window = tk.Toplevel(parent_window)
        self._window.title(self._config.title)

        geometry = f"{self._config.width}x{self._config.height}" \
            if self._config.height and self._config.width \
            else ""

        self._window.geometry(geometry)
        self._window.wm_attributes('-topmost', self._config.topmost)
        self._window.wm_attributes('-disabled', True)
        self._window.resizable(self._config.resizable, self._config.resizable)

        self._window.bind("<FocusIn>", functools.partial(
            self._on_focus_in, parent_window=parent_window))
        self._build_ui()

    def _clear_window(self) -> None:
        """Destroy all child widgets of the given window."""
        for widget in self._window.winfo_children():
            widget.destroy()

    @abstractmethod
    def _build_ui(self) -> None:
        pass

    def _on_show(self) -> None:
        pass

    def _on_focus_in(self, event: Any, parent_window: tk.Tk) -> None:
        parent_window.focus_force()

    def get_window(self) -> Optional[tk.Toplevel]:
        return self._window

    def hide(self) -> None:
        if self._window:
            if self._update_job:
                self._window.after_cancel(self._update_job)
                self._update_job = None
            self._window.withdraw()

    def destroy(self) -> None:
        if self._window:
            if self._update_job:
                self._window.after_cancel(self._update_job)
                self._update_job = None
            self._window.destroy()
            self._window = None
