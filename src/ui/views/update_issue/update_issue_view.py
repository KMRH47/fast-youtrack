import logging
from typing import Optional

import tkinter as tk
from tkinter import ttk

from services.youtrack_service import YouTrackService
from models.youtrack import (
    Issue,
    StateIssueCustomField,
    IssueFieldNames,
    IssueUpdateRequest,
    StateField,
    StateValue,
    BundleEnums,
)
from ui.views.base.custom_view_config import CustomViewConfig
from ui.views.base.custom_view import CustomView
from ui.windows.base.custom_window import CustomWindow

logger = logging.getLogger(__name__)


class UpdateIssueView(CustomView):
    def __init__(
        self,
        youtrack_service: YouTrackService,
        issue: Optional[Issue] = None,
        config: Optional[CustomViewConfig] = None,
    ):
        super().__init__(config=config)
        self.__youtrack_service = youtrack_service
        self.__issue: Optional[Issue] = issue
        self.selected_issue_state = tk.StringVar()
        self.issue_state_combobox = None

        self._update_view_state()

    def update_value(self, issue: Optional[Issue] = None) -> None:
        """Update the view with new issue details."""
        self.__issue = issue
        self._build_ui()
        self._update_view_state()
        self._flash_update(flash_color="red" if issue is None else "green")

    def _update_view_state(self) -> None:
        """Update the view's state based on the current issue."""
        if not self.issue_state_combobox:
            return

        if self.__issue is None:
            self.issue_state_combobox["values"] = []
            self.selected_issue_state.set("")
            self.issue_state_combobox.state(["disabled"])
        else:
            self.issue_state_combobox.state(["!disabled"])
            self._get_available_issue_states()

    def _populate_widgets(self, parent: tk.Frame) -> None:
        parent.grid_columnconfigure(0, weight=1)
        self._setup_ui(parent)

    def _setup_ui(self, parent: tk.Frame) -> None:
        self.issue_state_combobox = ttk.Combobox(
            parent,
            textvariable=self.selected_issue_state,
            state="readonly",
        )
        self.issue_state_combobox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.issue_state_combobox.bind("<<ComboboxSelected>>", self._on_state_changed)
        self._update_view_state()

    def _on_state_changed(self, _=None) -> None:
        if not self.__issue or not (selected_state := self.selected_issue_state.get()):
            return

        try:
            self._update_issue_state(selected_state)
        except Exception as e:
            logger.error(f"Error updating issue state: {e}")

    def _update_issue_state(self, selected_state: str) -> None:
        states = self.__youtrack_service.get_bundle(BundleEnums.STATE)
        state_bundle = next(state for state in states if state.name == selected_state)

        request = IssueUpdateRequest(
            fields=[StateField(value=StateValue(id=state_bundle.id))]
        )

        if not self.__youtrack_service.update_issue(self.__issue.id, request):
            return

        updated_issue = self.__youtrack_service.get_issue(self.__issue.id)
        if not updated_issue:
            return

        self.__issue = updated_issue

        if not isinstance(self.master, CustomWindow):
            return

        for view in self.master.get_attached_views():
            view.update_value(updated_issue)

    def _get_available_issue_states(self) -> None:
        if not self.issue_state_combobox:
            return

        try:
            states = self.__youtrack_service.get_bundle(BundleEnums.STATE)
            self.issue_state_combobox["values"] = [state.name for state in states]

            if not self.__issue or not self.__issue.fields:
                return

            def is_state_field(field):
                return (
                    isinstance(field, StateIssueCustomField)
                    and field.projectCustomField
                    and field.projectCustomField.field
                    and field.projectCustomField.field.name == IssueFieldNames.STATE
                )

            current_state = next(
                (field for field in self.__issue.fields if is_state_field(field)), None
            )

            if (
                current_state
                and current_state.value
                and current_state.value.name in self.issue_state_combobox["values"]
            ):
                self.selected_issue_state.set(current_state.value.name)

        except Exception as e:
            logger.error(f"Error fetching issue states: {e}")
