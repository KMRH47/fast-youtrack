import logging
import tkinter as tk

from datetime import datetime, time
from typing import Callable, Optional

from ui.widgets.custom_combobox import CustomComboboxConfig
from ui.widgets.custom_entry import CustomEntryConfig
from ui.windows.add_spent_time.add_spent_time_window_config import (
    AddSpentTimeWindowConfig,
)
from ui.windows.base.custom_window import CustomWindow
from utils.youtrack import time_valid
from ui.utils.create_labeled_widgets import (
    DATE_FORMAT_MAP,
    CustomDateEntryConfig,
    create_labeled_combobox,
    create_labeled_date_entry,
    create_labeled_entry,
)

logger = logging.getLogger(__name__)


class AddSpentTimeWindow(CustomWindow):
    def __init__(
        self,
        config: Optional[AddSpentTimeWindowConfig] = None,
        **kwargs,
    ):
        super().__init__(config=config, **kwargs)
        self.__issue_id_change_callback: Optional[Callable] = None
        self.__work_item_type_mapping: dict[str, str] = (
            config.work_item_types if config else {}
        )
        self.__config: Optional[AddSpentTimeWindowConfig] = config

        # StringVars
        self.__issue_id_var = tk.StringVar()
        self.__time_var = tk.StringVar()
        self.__description_var = tk.StringVar()
        self.__type_var = tk.StringVar()
        self.__date_var = tk.StringVar()

        initial_issue_id = (
            f"{config.project}{config.issue_separator}{config.initial_issue_id}"
        )

        # ID Entry
        self.__issue_id_var = create_labeled_entry(
            parent=self,
            label="Issue ID:",
            config=CustomEntryConfig(
                initial_value=initial_issue_id or "",
                break_chars=["-"],
                force_focus=True,
                cursor_end=True,
                on_change=self._on_issue_id_changed,
            ),
        )

        # Time Entry
        self.__time_var = create_labeled_entry(
            parent=self,
            label="Enter Time (e.g., 1h30m):",
            config=CustomEntryConfig(
                initial_value=config.initial_time or "",
                break_chars=["w", "d", "h", "m"],
                validation_func=lambda time: time_valid(time),
            ),
        )

        # Description Entry
        self.__description_var = create_labeled_entry(
            parent=self,
            label="Description:",
            config=CustomEntryConfig(initial_value=config.initial_description or ""),
        )

        # Type Entry
        self.__type_var = create_labeled_combobox(
            parent=self,
            label="Type:",
            config=CustomComboboxConfig(
                values=list(self.__work_item_type_mapping.keys()),
                initial_value=config.initial_type or "",
            ),
        )

        # Date Entry
        self.__date_var = create_labeled_date_entry(
            parent=self,
            label="Date:",
            config=CustomDateEntryConfig(
                initial_value=config.initial_date,
                date_format=config.date_format,
            ),
        )

        # OK Button
        ok_button = tk.Button(self, text="OK", command=self._submit, width=10)
        ok_button.pack(pady=5)

    def bind_issue_id_change(self, callback):
        """Bind a callback function to the issue ID change event."""
        self.__issue_id_change_callback = callback
        if self.__issue_id_var.get():
            self._on_issue_id_changed()

    def _submit(self, event=None):
        if time_valid(self.__time_var.get()):
            super()._submit(event)

    def _on_issue_id_changed(self, *args):
        issue_id = self.__issue_id_var.get().upper()
        self.__issue_id_var.set(issue_id)
        if self.__issue_id_change_callback:
            self.__issue_id_change_callback(issue_id)

    def _get_issue_id(self) -> str:
        return self.__issue_id_var.get()

    def _get_time(self) -> str:
        return self.__time_var.get()

    def _get_description(self) -> str:
        return self.__description_var.get()

    def _get_issue_type(self) -> str:
        selected_type_name = self.__type_var.get()
        return self.__work_item_type_mapping.get(selected_type_name)

    def _get_strptime_format(self, date_entry_format: str) -> str:
        return DATE_FORMAT_MAP.get(date_entry_format.lower())

    def _get_date_millis(self) -> Optional[int]:
        date_str = self.__date_var.get()
        try:
            strptime_format = self._get_strptime_format(self.__config.date_format)
            if not strptime_format:
                raise ValueError(
                    f"Unsupported date format: {self.__config.date_format}"
                )

            date_obj = datetime.strptime(date_str, strptime_format)
            timestamp = date_obj.timestamp() or int(time() * 1000)
            timestamp_millis = int(timestamp * 1000)
            logger.info(f"Date: {date_obj}, Timestamp: {timestamp_millis}")
            return timestamp_millis
        except ValueError as e:
            logger.error(f"Error parsing date: {e}")
            return None
