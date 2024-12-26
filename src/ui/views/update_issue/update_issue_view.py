import random
import re
import time
import logging
import tkinter as tk

from typing import List, Optional, Tuple
from tkinter import ttk

from pydantic import BaseModel

from services.youtrack_service import YouTrackService
from errors.user_cancelled_error import UserCancelledError
from models.general_responses import Issue, StateBundleElement
from models.general_requests import IssueUpdateRequest
from ui.views.base.custom_view_config import CustomViewConfig
from ui.views.issue_viewer.issue_viewer_view import IssueViewerView
from ui.views.timer.timer_view import TimerView
from ui.windows.base.custom_window import CustomWindow


logger = logging.getLogger(__name__)


class BundleEnums:
    STATE = "110-0"
    TYPE = "108-1"
    CATEGORY = "108-269"
    FIX_VERSIONS = "113-23"
    PROJECT_ID = "108-35"
    SUBSYSTEMS = "132-7"
    RESOLUTION = "108-198"
    BUILD_NUMBER = "133-1"
    PRIORITY = "108-0"


class IssueUpdate(BaseModel):
    id: str = ""
    time: str = ""
    description: str = ""
    state: str = ""
    type: str = ""


# INCOMPLETE AND NOT IN USE (basically just some old code I'm keeping for reference)
class UpdateIssueView:
    def __init__(self, youtrack_service: YouTrackService):
        self.__window = CustomWindow(
            config=CustomViewConfig(
                width=300, height=325, title="Update YouTrack Issue", topmost=True
            )
        )
        self.__youtrack_service = youtrack_service
        self.__cancelled = True
        self.__issue: Optional[Issue] = None
        self.__issue_update_request: Optional[IssueUpdateRequest] = None
        self.__issue_viewer = IssueViewerView(self.__window)
        self.__timer_view = TimerView(self.__window)
        self.debounce_id: Optional[str] = None
        self.selected_issue_state_var: Optional[tk.StringVar] = None
        self.issue_state_combobox: Optional[ttk.Combobox] = None
        self.issue_id_var: Optional[tk.StringVar] = None

    def show(self, issue_id: str = "") -> Tuple[Optional[IssueUpdateRequest], str]:
        # Issue State ComboBox
        tk.Label(self.__window, text="Current State:").pack(anchor="w", padx=10)
        self.selected_issue_state_var = tk.StringVar()
        self.issue_state_combobox = ttk.Combobox(
            self.__window,
            values=self._get_available_issue_states(),
            textvariable=self.selected_issue_state_var,
        )
        self.issue_state_combobox.pack(
            anchor="w", padx=10, pady=5, fill="x", expand=True
        )
        self.issue_state_combobox.bind(
            "<<ComboboxSelected>>", self._on_issue_state_change
        )
        self.issue_state_combobox.bind("<KeyRelease>", self._on_issue_state_change)

        # OK Button
        ok_button = tk.Button(
            self.__window, text="OK", command=self._on_submit, width=10
        )
        ok_button.pack(pady=5)

        logger.info("Prompting for issue update request...")

        # Test Attach
        timer_view = self.__timer_view._show()
        issue_view = self.__issue_viewer.show()

        self.__window.attach_window(timer_view.get_window(), position="top")

        self.__window.mainloop()

        if self.__cancelled:
            raise UserCancelledError()

        logger.info("issue update request: %s", self.__issue_update_request)

        return self.__issue_update_request, self.issue_id_var.get()

    def _on_issue_id_changed(self, *args):
        if self.debounce_id is not None:
            self.__window.after_cancel(self.debounce_id)

        issue_id = self.issue_id_var.get()

        if not issue_id_valid(issue_id):
            return

        def debounce():
            self.__issue = self.__youtrack_service.get_issue(issue_id)
            _get_issue_state = self._get_issue_state()
            self.selected_issue_state_var.set(_get_issue_state)
            if self.__issue_viewer:
                self.__issue_viewer.update_issue(self.__issue)

        self.debounce_id = self.__window.after(random.randint(253, 333), debounce)

    def _on_cancel(self, event=None):
        self.__window.destroy()

    def _get_issue_state(self) -> str:
        for field in self.__issue.fields:
            if field.projectCustomField and field.projectCustomField.bundle:
                if field.projectCustomField.bundle.id == BundleEnums.state:
                    return field.value.name

    def _get_available_issue_states(self):
        issue_states: list[StateBundleElement] = self.__youtrack_service.get_bundle(
            BundleEnums.state
        )
        return [state.name for state in issue_states if state.name]

    def _on_issue_state_change(self, event):
        logger.debug("Debouncing issue state change")

        if self.debounce_id:
            self.__window.after_cancel(self.debounce_id)

        def debounce():
            if not self._state_valid():
                self._apply_error_style(self.issue_state_combobox)
            else:
                self._reset_style(self.issue_state_combobox)
            self.issue_state_combobox["values"] = self._get_available_issue_states()

        self.debounce_id = self.__window.after(random.randint(253, 333), debounce)

    def _apply_error_style(self, widget):
        """Apply error styling to a widget."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Error.TCombobox", fieldbackground="white", bordercolor="red", borderwidth=2
        )
        widget.config(style="Error.TCombobox")

    def _reset_style(self, widget):
        """Reset the style of a widget to default."""
        widget.config(style="TCombobox")

    def _state_valid(self) -> bool:
        current_issue_state = self.selected_issue_state_var.get()
        return (
            current_issue_state is None
            or current_issue_state == ""
            or current_issue_state in self.issue_state_combobox["values"]
        )

    def _duration_valid(self) -> bool:
        time_entry_text = self.time_entry.get()
        duration_minutes = self._convert_time_to_minutes(time_entry_text)
        return duration_minutes is not None

    def _on_submit(self):
        try:
            self.__cancelled = False

            logger.info("Validating issue update request...")

            self.__issue_update_request = IssueUpdateRequest(
                summary=self.__issue.summary,
                description=self.__issue.description,
                fields=[],
                markdownEmbeddings=[],
                usesMarkdown=True,
            )

            for field in self.__issue.fields:
                updated_field_value = self.get_field_value_from_ui(field.id)

                if updated_field_value:

                    field.value.name = updated_field_value

                self.__issue_update_request.fields.append(field)

            logger.info("Valid issue update request.")
            self.__window.destroy()

        except Exception as e:
            logger.error(f"Error submitting issue: {e}")
            self.__window.destroy()
            raise e

    def get_field_value_from_ui(self, field_id):
        if field_id == "130-2":
            return self.ui_state_input.get()

        return None
