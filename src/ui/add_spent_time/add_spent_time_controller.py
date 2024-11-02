import logging
import random

from typing import Optional

from services.youtrack_service import YouTrackService
from models.general_requests import AddSpentTimeRequest
from models.general_responses import Issue
from utils.youtrack import id_valid
from ui.add_spent_time.add_spent_time_template import AddSpentTimeTemplate


logger = logging.getLogger(__name__)


class AddSpentTimeController:
    def __init__(self, youtrack_service: YouTrackService, issue_id: str = ""):
        self.__template = AddSpentTimeTemplate(issue_id)
        self.__youtrack_service = youtrack_service

        self.__issue: Issue | None = None
        self.__debounce_id: Optional[int] = None

    def show(self) -> tuple[str, Optional[AddSpentTimeRequest]]:
        return self.__template.show()

    def _on_issue_id_changed(self, *args):
        if self.__debounce_id is not None:
            self.__template.get_window().after_cancel(self.__debounce_id)

        issue_id = self.__template.get_issue_id()
        if not id_valid(issue_id):
            return

        def debounce():
            self.__issue = self.__youtrack_service.get_issue(issue_id)
            if self.__template.__issue_view:
                self.__template.__issue_view.update_issue(self.__issue)

        self.__debounce_id = self.__template.get_window().after(
            random.randint(253, 333), debounce)

    def _get_issue_state(self) -> str:
        for field in self.__issue.fields:
            if field.projectCustomField and field.projectCustomField.bundle:
                if field.projectCustomField.bundle.id == BundleEnums.state:
                    return field.value.name

    def get_field_value_from_ui(self, field_id):
        if field_id == '130-2':
            return self.ui_state_input.get()
        return None
