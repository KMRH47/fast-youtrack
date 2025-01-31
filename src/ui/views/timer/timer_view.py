import logging
import time
import tkinter as tk

from typing import Optional

from ui.views.base.custom_view import CustomView
from ui.views.base.custom_view_config import CustomViewConfig


logger = logging.getLogger(__name__)


class TimerView(CustomView):
    """
    A view that displays an elapsed time counter.
    """

    def __init__(self, config: Optional[CustomViewConfig] = None):
        super().__init__(config=config)
        self.__start_time: Optional[int] = None
        self.__timer_label: Optional[tk.Label] = None

    def _populate_widgets(self, parent: tk.Frame) -> None:
        """Populate widgets into the parent frame with timer details."""
        parent.config(bg=self._config.bg_color)

        self.__timer_label = tk.Label(
            parent,
            text="Elapsed Time: 00:00:00",
            font=("Arial", 14, "bold"),
            bg=self._config.bg_color,
            fg=self._config.text_color,
        )
        self.__timer_label.pack()

    def _on_show(self) -> None:
        if self.__start_time is not None:
            return
        self.__start_time = int(time.time())
        self._update_elapsed_time()

    def _update_elapsed_time(self) -> None:
        """Update the elapsed time label every second."""
        if not self.__start_time or not self.__timer_label:
            return

        elapsed = int(time.time()) - self.__start_time
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.__timer_label.config(
            text=f"Elapsed Time: {time_string}",
            bg=self._config.bg_color,
            fg=self._config.text_color,
        )
        self.after(1000, self._update_elapsed_time)

    def _reset(self):
        """Reset the timer to zero."""
        self.__start_time = int(time.time())
        self._update_elapsed_time()
