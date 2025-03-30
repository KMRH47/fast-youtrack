import logging
from datetime import date, datetime, timedelta
from typing import Optional

import tkinter as tk
from tkcalendar import DateEntry

from ui.widgets.custom_entry import CustomEntryConfig
from ui.constants.tk_events import TkEvents

logger = logging.getLogger(__name__)


class CustomDateEntryConfig(CustomEntryConfig):
    date_format: Optional[str]


class CustomDateEntry(DateEntry):
    DATE_FORMAT_MAP = {
        "dd/mm/yyyy": "%d/%m/%Y",
        "mm/dd/yyyy": "%m/%d/%Y",
        "yyyy/mm/dd": "%Y/%m/%d",
        "dd-mm-yyyy": "%d-%m-%Y",
        "mm-dd-yyyy": "%m-%d-%Y",
        "yyyy-mm-dd": "%Y-%m-%d",
    }

    def __init__(
        self, master, config: Optional[CustomDateEntryConfig] = None, **kwargs
    ):
        self.text_var = tk.StringVar()
        date_format = (
            config.date_format.lower()
        )

        super().__init__(
            master=master,
            textvariable=self.text_var,
            date_pattern=date_format,
            **kwargs,
        )

        if config and config.initial_value:
            try:
                strptime_format = self.DATE_FORMAT_MAP.get(date_format, "%Y-%m-%d")
                if config.initial_value == date_format:
                    initial_date = datetime.now()
                else:
                    initial_date = datetime.strptime(config.initial_value, strptime_format)
                self.set_date(initial_date)
            except ValueError as e:
                logger.error(f"Error parsing initial date: {e}")
                self.set_date(datetime.now())

        # bind arrow keys for going back and forth 1 day
        self.bind(TkEvents.LEFT_ARROW, lambda e: self._adjust_date(-1))
        self.bind(TkEvents.RIGHT_ARROW, lambda e: self._adjust_date(1))

    def _adjust_date(self, days: int) -> str:
        """Adjust date by given number of days, not allowing future dates."""
        new_date = self.get_date() + timedelta(days=days)
        if new_date <= date.today():
            self.set_date(new_date)
        return TkEvents.BREAK

    def get_date_millis(self) -> Optional[int]:
        """Returns the selected date in milliseconds since epoch."""
        date_object: date = self.get_date()
        datetime_object = datetime.combine(date_object, datetime.min.time())
        return int(datetime_object.timestamp() * 1000)

    def reset(self):
        """Reset the date to today."""
        self.set_date(date.today())