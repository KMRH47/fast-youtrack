import logging
from datetime import date, datetime
from typing import Optional

import tkinter as tk
from tkcalendar import DateEntry

from ui.widgets.custom_entry import CustomEntryConfig

logger = logging.getLogger(__name__)


class CustomDateEntryConfig(CustomEntryConfig):
    date_format: Optional[str] = "yyyy-mm-dd"


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
            if config and config.date_format
            else "yyyy-mm-dd"
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
                initial_date = datetime.strptime(config.initial_value, strptime_format)
                self.set_date(initial_date)
            except ValueError as e:
                logger.error(f"Error parsing initial date: {e}")

    def get_date_millis(self) -> Optional[int]:
        """Returns the selected date in milliseconds since epoch."""
        date_object: date = self.get_date()
        datetime_object = datetime.combine(date_object, datetime.min.time())
        return int(datetime_object.timestamp() * 1000)
