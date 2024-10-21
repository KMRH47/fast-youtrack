import logging
import re
import time
import tkinter as tk

from tkinter import ttk
from typing import Optional, Tuple

from services.youtrack_service import YouTrackService
from models.general_requests import IssueUpdateRequest
from models.general_responses import Issue
from errors.user_cancelled_error import UserCancelledError
from ui.issue_viewer import IssueView
from ui.timer_view import TimerView


logger = logging.getLogger(__name__)


class AddSpentTimeToIssueUI:
    def __init__(self, youtrack_service: YouTrackService):
        self.__window = tk.Tk()
        self.__window.title("Add Spent Time")
        self.__window.attributes('-topmost', True)
        self.__cancelled = True
        self.__youtrack_service = youtrack_service
        self.__issue: Issue | None = None
        self.__issue_update_request: IssueUpdateRequest | None = None
        self.__issue_viewer: IssueView | None = None

        # Intialize Viewers
        self.__timer_view = TimerView(self.__window)
        self.__issue_viewer = IssueView(self.__window)

        # Window size and position
        width = 300
        height = 325
        pos_right = int(self.__window.winfo_screenwidth() / 2 - width / 2)
        pos_down = int(self.__window.winfo_screenheight() / 2 - height / 2)
        self.__window.geometry(f"{width}x{height}+{pos_right}+{pos_down}")
        self.__window.resizable(False, False)

    def prompt(self, id: str = "") -> Tuple[Optional[IssueUpdateRequest], str]:
        # Bind "Escape" key to close the window
        self.__window.bind("<Escape>", self._on_cancel)
        self.__window.bind("<Return>", self._on_submit)

        # ID Text
        tk.Label(self.__window, text="Issue ID:").pack(
            anchor='w', padx=10, pady=5)
        # For observing changes to the ID
        self.__id_var = tk.StringVar()
        self.__id_var.trace_add(['write'], self._on_issue_id_changed)
        self.__id_var.set(id)

        # ID Entry
        self.__id_entry = tk.Entry(self.__window, textvariable=self.__id_var)
        self.__id_entry.pack(anchor='w', padx=10, fill='x', expand=True)
        self.__id_entry.icursor(tk.END)
        self.__id_entry.focus_force()

        # Time Text
        time_text = "Enter Time (e.g., 1h30m):"
        tk.Label(self.__window, text=time_text).pack(anchor='w', padx=10)

        # Time Entry
        self.__time_entry = tk.Entry(self.__window)
        self.__time_entry.pack(anchor='w', padx=10, fill='x', expand=True)

        # Description Text
        tk.Label(self.__window, text="Description:").pack(anchor='w', padx=10)

        # Description Entry
        self.__description_entry = tk.Entry(self.__window)
        self.__description_entry.pack(
            anchor='w', padx=10, pady=5, fill='x', expand=True)

        # Type Text
        tk.Label(self.__window, text="Type:").pack(anchor='w', padx=10)

        # Type Entry
        self.__type_entry = tk.Entry(self.__window)
        self.__type_entry.pack(anchor='w', padx=10, pady=5,
                               fill='x', expand=True)

        # OK Button
        ok_button = tk.Button(self.__window, text="OK",
                              command=self._on_submit, width=10)
        ok_button.pack(pady=5)

        # Bind Control-BackSpace for deleting words
        self.__id_entry.bind(
            '<Control-BackSpace>',
            lambda event: self._delete_word(event, ['-']))
        self.__time_entry.bind(
            '<Control-BackSpace>',
            lambda event: self._delete_word(event, ['d', 'h', 'm']))
        self.__description_entry.bind(
            '<Control-BackSpace>',
            lambda event: self._delete_word(event, []))
        self.__type_entry.bind('<Control-BackSpace>',
                               lambda event: self._delete_word(event, []))

        logger.info("Prompting for issue update request...")


        self.__window.mainloop()

        if self.__cancelled:
            raise UserCancelledError()

        logger.info("issue update request: %s", self.__issue_update_request)

        return self.__issue_update_request, self.__id_var.get()

    def _on_issue_id_changed(self, *args):
        id = self.__id_var.get()

        if not id_valid(id):
            return

        self.__issue_viewer.update_issue(self.__issue)

    def _get_issue_state(self) -> str:
        for field in self.__issue.fields:
            if field.projectCustomField and field.projectCustomField.bundle:
                if field.projectCustomField.bundle.id == BundleEnums.state:
                    return field.value.name


def id_valid(issue_id: str) -> bool:
    return re.match(r"^[A-Za-z]+-\d+$", issue_id)
