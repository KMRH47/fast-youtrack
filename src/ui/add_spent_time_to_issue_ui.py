import logging
import re
import time
import tkinter as tk

from tkinter import ttk
from typing import List, Optional, Tuple

from services.youtrack_service import YouTrackService
from models.general_requests import AddSpentTimeRequest, IssueUpdateRequest
from models.general_responses import Issue
from errors.user_cancelled_error import UserCancelledError
from ui.custom.custom_window import CustomWindow, CustomWindowConfig
from ui.custom.custom_entry import CustomEntry, CustomEntryConfig
from ui.issue_viewer import IssueView
from ui.timer_view import TimerView


logger = logging.getLogger(__name__)


class AddSpentTimeToIssueUI:
    def __init__(self, youtrack_service: YouTrackService):
        self.__window = CustomWindow(config=CustomWindowConfig(
            width=300, height=325, title="Add Spent Time", topmost=True, close_on_cancel=False))
        self.__cancelled = True
        self.__youtrack_service = youtrack_service
        self.__issue: Issue | None = None
        self.__issue_update_request: IssueUpdateRequest | None = None

        # Intialize Read-only UIs
        self.__timer_view = TimerView(self.__window)
        self.__issue_view = IssueView(self.__window)

    def show(self, id: str = "") -> Tuple[Optional[IssueUpdateRequest], str]:
        # ID Text
        tk.Label(self.__window, text="Issue ID:").pack(
            anchor='w', padx=10, pady=5)
        self.__id_var = tk.StringVar()
        self.__id_var.trace_add(['write'], self._on_issue_id_changed)
        self.__id_var.set(id)
        self.__id_entry = CustomEntry(
            self.__window, textvariable=self.__id_var, config=CustomEntryConfig(['-']))
        self.__id_entry.pack(anchor='w', padx=10, fill='x', expand=True)
        self.__id_entry.icursor(tk.END)
        self.__id_entry.focus_force()

        # Time
        time_text = "Enter Time (e.g., 1h30m):"
        tk.Label(self.__window, text=time_text).pack(anchor='w', padx=10)
        self.__time_entry = CustomEntry(
            self.__window, config=CustomEntryConfig(break_chars=['w', 'd', 'h', 'm']))
        self.__time_entry.pack(anchor='w', padx=10, fill='x', expand=True)

        # Description
        tk.Label(self.__window, text="Description:").pack(anchor='w', padx=10)
        self.__description_entry = CustomEntry(self.__window)
        self.__description_entry.pack(
            anchor='w', padx=10, pady=5, fill='x', expand=True)

        # Type
        tk.Label(self.__window, text="Type:").pack(anchor='w', padx=10)
        self.__type_entry = CustomEntry(self.__window)
        self.__type_entry.pack(anchor='w', padx=10, pady=5,
                               fill='x', expand=True)

        # OK Button
        ok_button = tk.Button(self.__window, text="OK",
                              command=self._on_submit, width=10)
        ok_button.pack(pady=5)

        logger.info("Prompting for issue update request...")

        timer_view = self.__timer_view.show()
        issue_view = self.__issue_view.show()
        self.__window.attach_window(issue_view, position="top")
        self.__window.attach_window(timer_view, position="top")

        self.__window.mainloop()

        if self.__cancelled:
            raise UserCancelledError()

        logger.info("issue update request: %s", self.__issue_update_request)

        return self.__issue_update_request, self.__id_var.get()

    def _on_submit(self):
        try:
            self.__cancelled = False

            logger.info("Validating issue update request...")

            self.__issue_update_request = AddSpentTimeRequest(
                description=self.__description_entry.get(),
                time=self.__time_entry.get(),
                type=self.__type_entry.get(),
            )

            self.__window.destroy()

        except Exception as e:
            logger.error(
                f"Error adding spent time to issue: {self.__id_var.get()}")
            self.__window.destroy()
            raise e

    def _on_issue_id_changed(self, *args):
        id = self.__id_var.get()

        if not id_valid(id):
            return

        self.__issue_view.update_issue(self.__issue)

    def _get_issue_state(self) -> str:
        for field in self.__issue.fields:
            if field.projectCustomField and field.projectCustomField.bundle:
                if field.projectCustomField.bundle.id == BundleEnums.state:
                    return field.value.name

    def get_field_value_from_ui(self, field_id):
        if field_id == '130-2':
            return self.ui_state_input.get()
        return None

    def _convert_time_to_minutes(self, time_str: str) -> int | None:
        def extract_time(unit: str) -> int:
            match = re.search(rf"(\d+){unit}", time_str.strip())
            return int(match.group(1)) if match else 0

        days_in_minutes = extract_time('d') * 24 * 60
        hours_in_minutes = extract_time('h') * 60

        total_minutes = days_in_minutes + hours_in_minutes + extract_time('m')

        return total_minutes if total_minutes > 0 else None


def id_valid(issue_id: str) -> bool:
    return re.match(r"^[A-Za-z]+-\d+$", issue_id)
