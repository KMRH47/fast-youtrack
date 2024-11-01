import random
import re
import time
import logging
import tkinter as tk

from typing import List, Optional, Tuple
from tkinter import ttk

from services.youtrack_service import YouTrackService
from errors.user_cancelled_error import UserCancelledError
from models.general_responses import Issue, StateBundleElement
from models.issue_states import BundleEnums
from models.general_requests import IssueUpdateRequest
from ui.custom.custom_window import CustomWindow, CustomWindowConfig
from ui.timer_view import TimerView


logger = logging.getLogger(__name__)


class IssueUpdateRequestUI:
    def __init__(self, youtrack_service: YouTrackService):
        self.__window = CustomWindow(
            config=CustomWindowConfig(width=300, height=325, title="Update YouTrack Issue", topmost=True))
        self.__youtrack_service = youtrack_service
        self.__cancelled = True
        self.__issue: Issue | None = None
        self.__issue_update_request: IssueUpdateRequest | None = None
        self.__issue_viewer = IssueView(self.__window)
        self.__timer_view = TimerView(self.__window)

    def show(self, issue_id: str = "") -> Tuple[Optional[IssueUpdateRequest], str]:
        # Issue State ComboBox
        tk.Label(self.__window, text="Current State:").pack(
            anchor='w', padx=10)
        self.selected_issue_state_var = tk.StringVar()
        self.issue_state_combobox = ttk.Combobox(
            self.__window,
            values=self._get_available_issue_states(),
            textvariable=self.selected_issue_state_var)
        self.issue_state_combobox.pack(
            anchor='w', padx=10, pady=5, fill='x', expand=True)
        self.issue_state_combobox.bind(
            '<<ComboboxSelected>>', self._on_issue_state_change)
        self.issue_state_combobox.bind(
            '<KeyRelease>', self._on_issue_state_change)

        # OK Button
        ok_button = tk.Button(self.__window, text="OK",
                              command=self._on_submit, width=10)
        ok_button.pack(pady=5)

        logger.info("Prompting for issue update request...")

        # Test Attach
# Test Attach
        timer_view = self.__timer_view.show()  # Now timer_view is a TimerView object
        issue_view = self.__issue_viewer.show()  # issue_view is an IssueView object

        # Attach the windows using the TimerView and IssueView objects
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

        self.debounce_id = self.__window.after(
            random.randint(253, 333), debounce)

    def _on_cancel(self, event=None):
        self.__window.destroy()

    def _get_issue_state(self) -> str:
        for field in self.__issue.fields:
            if field.projectCustomField and field.projectCustomField.bundle:
                if field.projectCustomField.bundle.id == BundleEnums.state:
                    return field.value.name

    def _get_available_issue_states(self):
        issue_states: list[StateBundleElement] = \
            self.__youtrack_service.get_bundle(BundleEnums.state)
        return [state.name for state in issue_states if state.name]

    def _on_issue_state_change(self, event):
        if self.debounce_id:
            self.__window.after_cancel(self.debounce_id)

        def debounce():
            if not self._state_valid():
                self._apply_error_style(self.issue_state_combobox)
            else:
                self._reset_style(self.issue_state_combobox)
            self.issue_state_combobox['values'] = \
                self._get_available_issue_states()

        self.debounce_id = self.__window.after(
            random.randint(253, 333), debounce)

    def _apply_error_style(self, widget):
        """Apply error styling to a widget."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Error.TCombobox', fieldbackground='white',
                        bordercolor='red', borderwidth=2)
        widget.config(style='Error.TCombobox')

    def _reset_style(self, widget):
        """Reset the style of a widget to default."""
        widget.config(style='TCombobox')

    def _state_valid(self) -> bool:
        current_issue_state = self.selected_issue_state_var.get()
        return (
            current_issue_state is None or current_issue_state == "" or
            current_issue_state in self.issue_state_combobox['values']
        )

    def _duration_valid(self) -> bool:
        time_entry_text = self.time_entry.get()
        duration_minutes = self._convert_time_to_minutes(time_entry_text)
        return duration_minutes is not None

    def _on_submit(self):
        try:
            self.__cancelled = False

            logger.info("Validating issue update request...")

            # Create the base update request using the issue response
            self.__issue_update_request = IssueUpdateRequest(
                summary=self.__issue.summary,  # Use the current summary from the issue response
                # Use the current description from the issue response
                description=self.__issue.description,
                fields=[],  # We will populate this with updated fields later
                # UI data for markdown embeddings (assuming this is UI input)
                markdownEmbeddings=[],
                # UI input (assuming this is a toggle or similar in the UI)
                usesMarkdown=True
            )

            # Handling the fields: use the response data to keep fields in sync
            for field in self.__issue.fields:
                # Here we could have logic to check if fields were updated in the UI
                updated_field_value = self.get_field_value_from_ui(
                    field.id)  # This is a placeholder method

                if updated_field_value:
                    # Override the field value from the UI
                    field.value.name = updated_field_value

                # Append the field to the update request's fields
                self.__issue_update_request.fields.append(field)

            logger.info("Valid issue update request.")
            self.__window.destroy()

        except Exception as e:
            logger.error(f"Error submitting issue: {e}")
            self.__window.destroy()
            raise e

    def get_field_value_from_ui(self, field_id):
        # Example logic to get the value of a field from the UI by field id
        if field_id == '130-2':  # Let's say this is the field for state
            return self.ui_state_input.get()  # Fetch the value from a UI field
        # Add additional field checks as necessary
        return None  # Return None if no update is found in the UI for the field
