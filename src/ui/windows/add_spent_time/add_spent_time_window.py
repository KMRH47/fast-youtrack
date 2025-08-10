import logging
from typing import Callable, List, Optional

import tkinter as tk

from models.general_responses import WorkItem
from ui.widgets.custom_combobox import CustomComboboxConfig
from ui.widgets.custom_entry import CustomEntryConfig
from ui.windows.add_spent_time.add_spent_time_window_config import (
    AddSpentTimeWindowConfig,
)
from ui.windows.base.custom_window import CustomWindow
from utils.youtrack import time_valid
from ui.utils.create_labeled_widgets import (
    CustomDateEntryConfig,
    create_labeled_combobox,
    create_labeled_compound_entry,
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

        (
            self.__project_var,
            self.__id_var,
            self.__project_entry,
            self.__id_entry,
        ) = create_labeled_compound_entry(
            parent=self,
            label="Issue:",
            left_value=config.project or "",
            right_value=config.initial_issue_id or "",
            separator="-",
            left_width=4,
            left_readonly=True,
            on_change=self._on_issue_id_changed,
            focus_right=True,
        )

        self.__time_entry = create_labeled_entry(
            parent=self,
            label="Enter Time (e.g., 1h30m):",
            config=CustomEntryConfig(
                initial_value=config.initial_time or "",
                break_chars=["w", "d", "h", "m"],
                validation_func=lambda time: time_valid(time),
            ),
        )

        self.__description_entry = create_labeled_entry(
            parent=self,
            label="Description:",
            config=CustomEntryConfig(initial_value=config.initial_description or ""),
        )

        self.__type_combobox = create_labeled_combobox(
            parent=self,
            label="Type:",
            config=CustomComboboxConfig(
                values=config.work_item_types,
                initial_value=config.initial_type or "",
            ),
        )

        self.__date_entry = create_labeled_date_entry(
            parent=self,
            label="Date:",
            config=CustomDateEntryConfig(
                initial_value=config.initial_date,
                date_format=config.date_format,
            ),
        )

        ok_button = tk.Button(self, text="OK", command=self._submit, width=10)
        ok_button.pack(pady=5)

    def bind_issue_id_change(self, callback):
        self.__issue_id_change_callback = callback
        if self.__project_entry.get() or self.__id_entry.get():
            self._on_issue_id_changed()

    def _submit(self, event=None):
        if not time_valid(self.__time_entry.get()):
            return

        super()._submit(event)
        self._reset()

    def _on_issue_id_changed(self, *_):
        project = (self.__project_entry.get() or "").strip().upper()
        raw_id = (self.__id_entry.get() or "").strip().upper()
        sep = "-"
        issue_id = (
            f"{project}{sep}{raw_id}" if project and raw_id else (project or raw_id)
        )
        if self.__issue_id_change_callback:
            self.__issue_id_change_callback(issue_id)

    def _get_issue_id(self) -> str:
        project = (self.__project_entry.get() or "").strip().upper()
        raw_id = (self.__id_entry.get() or "").strip().upper()
        sep = "-"
        return f"{project}{sep}{raw_id}" if project and raw_id else (project or raw_id)

    def _get_time(self) -> str:
        return self.__time_entry.get()

    def _get_description(self) -> str:
        return self.__description_entry.get()

    def _get_selected_issue_type(self) -> str:
        return self.__type_combobox.get()

    def _get_date_millis(self) -> Optional[int]:
        return self.__date_entry.get_date_millis()

    def _set_issue_types(self, work_item_types: List[WorkItem]):
        updated_work_item_types = [
            work_item_type.name for work_item_type in work_item_types
        ]

        if updated_work_item_types == self.__type_combobox["values"]:
            return

        if self._get_selected_issue_type() not in [wt.id for wt in work_item_types]:
            self.__type_combobox.set("")

        self.__type_combobox.configure(values=updated_work_item_types)

    def _on_window_close(self, event=None):
        self._reset()
        super()._on_window_close(event)

    def _reset(self):
        self.__project_var.set(f"{self._config.project}")
        self.__id_var.set("")
        self.__id_entry.focus_set()
        self.__date_entry.reset()
        self.__time_entry.reset()
        self.__description_entry.reset()
        self.__type_combobox.set("")

        self._reset_attached_views()
