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

        # grid
        parent.grid_columnconfigure(0, weight=0, minsize=50)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=0, minsize=50)

        # timer text
        self.__timer_label = tk.Label(
            parent,
            text="00:00:00",
            font=("Arial", 14, "bold"),
            bg=self._config.bg_color,
            fg=self._config.text_color,
        )
        self.__timer_label.grid(row=0, column=1, sticky="nsew")

        # reset button
        self.__reset_button = tk.Button(
            parent,
            text="Reset",
            command=self._reset,
            bg=self._config.bg_color,
            fg=self._config.text_color,
            takefocus=False,
        )
        self.__reset_button.grid(row=0, column=2, sticky="e", padx=5)

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
            text=f"{time_string}",
            bg=self._config.bg_color,
            fg=self._config.text_color,
        )
        self.after(1000, self._update_elapsed_time)

    def _reset(self):
        """Reset the timer to zero."""
        self.__start_time = int(time.time())
        self._update_elapsed_time()
