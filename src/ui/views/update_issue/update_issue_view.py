import logging
from typing import Optional

import tkinter as tk

from services.youtrack_service import YouTrackService
from models.youtrack import (
    BundleEnums,
    Issue,
    IssueUpdateRequest,
    StateField,
    StateIssueCustomField,
    StateValue,
)
from ui.views.base.custom_view_config import CustomViewConfig
from ui.views.base.custom_view import CustomView
from ui.widgets.custom_combobox import CustomComboboxConfig
from ui.utils.create_labeled_widgets import create_labeled_combobox

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
        self.__issue = issue

    def update_value(self, issue: Optional[Issue] = None) -> None:
        self.__issue = issue
        self._update_issue_state_combobox()
        self._flash_update(flash_color="red" if issue is None else "green")

    def _populate_widgets(self, parent: tk.Frame) -> None:
        self.__issue_state_combobox = create_labeled_combobox(
            parent=parent,
            label="State:",
            config=CustomComboboxConfig(values={}, initial_value=""),
        )
        self.__issue_state_combobox.state(["disabled"])
        self.__issue_state_combobox.bind(
            "<<ComboboxSelected>>", lambda _: self._on_issue_state_changed()
        )

    def _on_issue_state_changed(self) -> None:
        selected_state = self.__issue_state_combobox.get()
        if not self.__issue or not selected_state:
            return

        if not (updated_issue := self._update_issue_state(selected_state)):
            return

        self.__issue = updated_issue
        self._notify_views(updated_issue)

    def _update_issue_state(self, new_state: str) -> Optional[Issue]:
        states = self.__youtrack_service.get_bundle(BundleEnums.STATE)
        state_bundle = next(
            (state for state in states if state.name == new_state), None
        )
        if not state_bundle:
            return None

        request = IssueUpdateRequest(
            fields=[StateField(value=StateValue(id=state_bundle.id))]
        )

        if not self.__youtrack_service.update_issue(self.__issue.id, request):
            return None

        return self.__youtrack_service.get_issue(self.__issue.id)

    def _notify_views(self, issue: Issue) -> None:
        for view in self.window.get_attached_views():
            view.update_value(issue)

    def _update_issue_state_combobox(self) -> None:
        states = self.__youtrack_service.get_bundle(BundleEnums.STATE)
        state_names = [state.name for state in states]
        current_state = self._get_current_issue_state(state_names)

        self.__issue_state_combobox["values"] = state_names
        self.__issue_state_combobox.set(current_state or "")
        self.__issue_state_combobox.configure(
            state="readonly" if self.__issue and self.__issue.fields else "disabled"
        )

    def _get_current_issue_state(self, valid_states: list[str]) -> Optional[str]:
        if not self.__issue or not self.__issue.fields:
            return None

        for field in self.__issue.fields:
            if not isinstance(field, StateIssueCustomField):
                continue

            if not field.value or field.value.name not in valid_states:
                continue

            return field.value.name

        return None
