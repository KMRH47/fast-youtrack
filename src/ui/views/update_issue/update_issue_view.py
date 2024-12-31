import logging
from typing import Optional

import tkinter as tk
from tkinter import ttk

from services.youtrack_service import YouTrackService
from models.youtrack import Issue, StateIssueCustomField, IssueFieldNames, IssueUpdateRequest
from ui.views.base.custom_view_config import CustomViewConfig
from ui.views.base.custom_view import CustomView

logger = logging.getLogger(__name__)

# Constants
ERROR_COLOR = "red"
SUCCESS_COLOR = "green"
LOADING_MESSAGE = "Loading..."


class BundleEnums:
    STATE = "110-0"


class UpdateIssueView(CustomView):
    def __init__(
        self,
        youtrack_service: YouTrackService,
        config: Optional[CustomViewConfig] = None,
    ):
        super().__init__(config=config)
        self.__youtrack_service = youtrack_service
        self.__issue: Optional[Issue] = None
        self.__issue_update_request: Optional[IssueUpdateRequest] = None
        self.selected_issue_state_var: Optional[tk.StringVar] = None
        self.issue_state_combobox: Optional[ttk.Combobox] = None
        self.submit_button: Optional[tk.Button] = None
        self.error_label: Optional[tk.Label] = None

    def _populate_widgets(self, parent: tk.Frame) -> None:
        """Build the UI components."""
        parent.config(bg=self._config.bg_color)

        # Issue State ComboBox
        tk.Label(parent, text="Current State:", bg=self._config.bg_color).pack(
            anchor="w", padx=10
        )
        self.selected_issue_state_var = tk.StringVar()
        self.issue_state_combobox = ttk.Combobox(
            parent,
            values=[LOADING_MESSAGE],
            textvariable=self.selected_issue_state_var,
            state=tk.DISABLED,
        )
        self.issue_state_combobox.pack(
            anchor="w", padx=10, pady=5, fill="x", expand=True
        )

        # Bind events
        self.issue_state_combobox.bind("<<ComboboxSelected>>", self._on_submit)

        # Submit Button (initially disabled)
        self.submit_button = tk.Button(
            parent, text="Update", command=self._on_submit, width=10, state=tk.DISABLED
        )
        self.submit_button.pack(pady=5)

        # Error Label
        self.error_label = tk.Label(
            parent, text="", fg=ERROR_COLOR, bg=self._config.bg_color
        )
        self.error_label.pack()

        # Load states after UI is built
        self._get_available_issue_states()

    def update_value(self, issue: Optional[Issue] = None) -> None:
        """Update the view with new issue details."""
        self.__issue = issue
        if hasattr(self, "selected_issue_state_var"):
            self.selected_issue_state_var.set("")
        if hasattr(self, "error_label"):
            self.error_label.config(text="")

        self._build_ui()
        if issue:
            self.update_idletasks()
            self._flash_update(flash_color=SUCCESS_COLOR)

    def _on_submit(self) -> None:
        """Handle form submission."""
        try:
            selected_state = self.selected_issue_state_var.get()
            states = self.__youtrack_service.get_bundle(BundleEnums.STATE)
            state_bundle = next(s for s in states if s.name == selected_state)

            self.__issue_update_request = IssueUpdateRequest(
                fields=[
                    {
                        "name": "State",
                        "$type": "StateIssueCustomField",
                        "value": {
                            "name": state_bundle.name,
                            "id": state_bundle.id,
                            "$type": "StateBundleElement",
                        },
                    }
                ]
            )

            self.__youtrack_service.update_issue(
                self.__issue.id, self.__issue_update_request
            )
            self._flash_update(flash_color=SUCCESS_COLOR)
            self.master.destroy()

        except Exception as e:
            logger.error(f"Error submitting issue update: {e}")
            self.error_label.config(text=f"Error: {str(e)}")
            self._flash_update(flash_color=ERROR_COLOR)

    def _get_available_issue_states(self) -> None:
        """Get available states and update the combobox."""
        try:
            states = self.__youtrack_service.get_bundle(BundleEnums.STATE)
            state_names = [state.name for state in states]
            self.issue_state_combobox["values"] = state_names
            self.issue_state_combobox["state"] = "readonly"

            if not self.__issue or not self.__issue.fields:
                return

            state_field = next(
                (
                    field
                    for field in self.__issue.fields
                    if isinstance(field, StateIssueCustomField)
                    and field.projectCustomField
                    and field.projectCustomField.field
                    and field.projectCustomField.field.name == IssueFieldNames.STATE
                ),
                None,
            )

            if (
                state_field
                and state_field.value
                and state_field.value.name in state_names
            ):
                self.selected_issue_state_var.set(state_field.value.name)

        except Exception as e:
            logger.error(f"Error fetching issue states: {e}")
            self.error_label.config(text=f"Error: {str(e)}")
