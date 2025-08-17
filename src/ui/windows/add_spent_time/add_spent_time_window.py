import logging
import time
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

        self.__work_item_name_to_id = {}

        self.__last_activity_time = time.time()
        self.__date_manually_edited = False

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

        try:
            self.__id_var.trace_add("write", self._sanitize_id_var)
        except Exception:
            pass

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

        self.__date_entry.bind("<KeyPress>", self._on_date_manual_edit)
        self.__date_entry.bind("<Button-1>", self._on_date_manual_edit)

        ok_button = tk.Button(self, text="OK", command=self._submit, width=10)
        ok_button.pack(pady=5)

        self.bind("<FocusIn>", self._on_window_focus)
        self.bind("<Button-1>", lambda e: self._update_activity_time())
        self.bind("<Key>", lambda e: self._update_activity_time())

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

    def _prefill_issue_id(self, text: str) -> bool:
        """Prefill the right-side issue id entry from arbitrary text. Returns True if applied."""
        import re

        cleaned_text: str = (text or "").strip()
        if not cleaned_text:
            return False

        uppercase_text: str = cleaned_text.upper()
        key_match = re.search(r"\b([A-Z]{2,})[- ]?(\d+)\b", uppercase_text)
        if key_match:
            project_code: str = key_match.group(1)
            numeric_issue_id: str = key_match.group(2)
            self.__project_var.set(project_code)
            self.__id_var.set(numeric_issue_id)
            self._on_issue_id_changed()
            return True

        numeric_tokens = re.findall(r"\d+", cleaned_text)
        if not numeric_tokens:
            return False

        numeric_issue_id = max(numeric_tokens, key=len)
        self.__id_var.set(numeric_issue_id)
        self._on_issue_id_changed()
        return True

    def handle_hotkey_activation(self, selected_text: str) -> None:
        if selected_text and self._prefill_issue_id(selected_text):
            self._focus_time_field()
            return
        self._focus_issue_id_field()

    def _focus_issue_id_field(self) -> None:
        self.lift()
        try:
            self.focus_force()
        except Exception:
            pass
        self.__id_entry.focus_set()

    def _focus_time_field(self) -> None:
        self.lift()
        try:
            self.focus_force()
        except Exception:
            pass
        self.__time_entry.focus_force()

    def _sanitize_id_var(self, *_args: object) -> None:
        raw_issue_id_text: str = self.__id_var.get()
        digits_only_text: str = "".join(ch for ch in raw_issue_id_text if ch.isdigit())
        if digits_only_text != raw_issue_id_text:
            self.__id_var.set(digits_only_text)

    def _get_time(self) -> str:
        return self.__time_entry.get()

    def _get_description(self) -> str:
        return self.__description_entry.get()

    def _get_selected_issue_type(self) -> str:
        return self.__type_combobox.get()

    def _get_selected_issue_type_id(self) -> Optional[str]:
        """Get the ID of the selected work item type."""
        selected_name = self.__type_combobox.get()
        return self.__work_item_name_to_id.get(selected_name)

    def _get_date_millis(self) -> Optional[int]:
        return self.__date_entry.get_date_millis()

    def _set_issue_types(self, work_item_types: List[WorkItem]):
        updated_work_item_types = [
            work_item_type.name for work_item_type in work_item_types
        ]

        if updated_work_item_types == self.__type_combobox["values"]:
            return

        self.__work_item_name_to_id = {wt.name: wt.id for wt in work_item_types}

        if self._get_selected_issue_type() not in [wt.name for wt in work_item_types]:
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

        self.__date_manually_edited = False
        self._update_activity_time()

        self._reset_attached_views()

    def _on_date_manual_edit(self, event=None):
        """Pin date auto-updates when user manually edits."""
        self.__date_manually_edited = True

    def _update_activity_time(self):
        """Update last activity timestamp."""
        self.__last_activity_time = time.time()

    def _is_afk(self, threshold_minutes=5) -> bool:
        """Check if user has been AFK for threshold minutes."""
        return (time.time() - self.__last_activity_time) > (threshold_minutes * 60)

    def _maybe_update_date_after_afk(self):
        """Auto-update date if AFK and not pinned/focused."""
        if self.__date_manually_edited:
            return

        if self.focus_get() == self.__date_entry:
            return

        if self._is_afk():
            self.__date_entry.reset()

    def _on_window_focus(self, event=None):
        """Handle window getting focus - check for date update."""
        self._maybe_update_date_after_afk()
        self._update_activity_time()
