import logging
import tkinter as tk
from typing import Literal, Optional, TypeVar

from ui.custom.custom_view_config import CustomViewConfig

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CustomView(tk.Toplevel):
    __position: Literal["left", "right", "top", "bottom"] = "right"

    def __init__(
        self,
        parent_window: Optional[tk.Tk] = None,
        config: CustomViewConfig = CustomViewConfig(),
    ):
        super().__init__(master=parent_window)
        self._config = config
        self.__position = config.position
        self._update_job: Optional[str] = None

    def update_value(self, value: T) -> None:
        """Update the view with a new value.
        Note: This method is expected to be overridden by subclasses to use `value`.
        """
        pass

    def _show(self, parent_window: tk.Tk) -> None:
        self._create_window(parent_window)
        self.transient(parent_window)
        self.update_idletasks()
        self._on_show()

    def _hide(self) -> None:
        if self._update_job:
            self.after_cancel(self._update_job)
            self._update_job = None
        self.withdraw()

    def _destroy(self) -> None:
        if self._update_job:
            self.after_cancel(self._update_job)
            self._update_job = None
        self.destroy()
        self = None

    def _create_window(self, parent_window: tk.Tk) -> None:
        self.master = parent_window
        self.title(self._config.title)

        geometry = (
            f"{self._config.width}x{self._config.height}"
            if self._config.height and self._config.width
            else ""
        )

        self.geometry(geometry)
        self.wm_attributes("-topmost", self._config.topmost)
        self.wm_attributes("-disabled", True)
        self.resizable(self._config.resizable, self._config.resizable)

        self._build_ui()

    def _clear_window(self) -> None:
        """Destroy all child widgets of the given window."""
        for widget in self.winfo_children():
            widget.destroy()

    def _build_ui(self) -> None:
        self._clear_window()

        self.geometry("")
        container_frame = tk.Frame(self, padx=10, pady=10)
        container_frame.pack(fill="both", expand=True)
        self._populate_widgets(container_frame)

    def _set_position(
        self, position: Literal["left", "right", "top", "bottom"]
    ) -> None:
        self.__position = position

    def _get_position(self) -> Literal["left", "right", "top", "bottom"]:
        return self.__position

    def _populate_widgets(self, parent: tk.Frame) -> None:
        pass

    def _on_show(self) -> None:
        pass
