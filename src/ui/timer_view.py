import logging
import time
import tkinter as tk
from typing import Optional

from ui.custom.custom_window_config import CustomWindowConfig
from ui.custom.custom_toplevel import CustomTopLevel

logger = logging.getLogger(__name__)


class TimerView(CustomTopLevel):
    """
    A window that displays an elapsed time counter.
    Inherits window management functionality from BaseTopLevelView.
    """

    def __init__(self, config: Optional[CustomWindowConfig] = None):
        super().__init__(config)
        self.__start_time: Optional[int] = None
        self.__timer_label: Optional[tk.Label] = None
        self.__update_job: Optional[str] = None

    def _build_ui(self) -> None:
        """Build the timer UI elements."""
        window = self.get_window()
        if not window:
            return

        container_frame = tk.Frame(window, padx=10, pady=10)
        container_frame.pack(fill='both', expand=True)

        self.__timer_label = tk.Label(
            container_frame,
            text="Elapsed Time: 00:00:00",
            font=("Arial", 14, "bold")
        )
        self.__timer_label.pack()

    def _on_show(self) -> None:
        """
        Override base _on_show to start the timer when window is displayed.
        Called automatically by the base class show() method.
        """
        self.__start_time = int(time.time())
        self._update_elapsed_time()

    def _update_elapsed_time(self) -> None:
        """Update the elapsed time label every second."""
        if not self.__start_time or not self.__timer_label or not self.get_window():
            return

        elapsed = int(time.time()) - self.__start_time
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.__timer_label.config(text=f"Elapsed Time: {time_string}")

        # Schedule next update if window exists
        window = self.get_window()
        if window:
            self.__update_job = window.after(1000, self._update_elapsed_time)

    def reset_timer(self) -> None:
        """Reset the timer to zero."""
        self.__start_time = int(time.time())
        self._update_elapsed_time()

    def get_elapsed_time(self) -> int:
        """Get the current elapsed time in seconds."""
        if self.__start_time is None:
            return 0
        return int(time.time()) - self.__start_time

    def destroy(self) -> None:
        """
        Override destroy to cancel any pending timer updates 
        before destroying the window.
        """
        window = self.get_window()
        if window and self.__update_job:
            window.after_cancel(self.__update_job)
            self.__update_job = None

        super().destroy()

    def hide(self) -> None:
        """
        Override hide to cancel any pending timer updates 
        before hiding the window.
        """
        window = self.get_window()
        if window and self.__update_job:
            window.after_cancel(self.__update_job)
            self.__update_job = None

        super().hide()
