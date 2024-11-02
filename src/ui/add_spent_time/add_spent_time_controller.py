import random
from typing import Optional
from services.youtrack_service import YouTrackService
from models.general_requests import AddSpentTimeRequest
from ui.add_spent_time.add_spent_time_template import AddSpentTimeTemplate
from ui.issue_view import IssueView
from ui.timer_view import TimerView
from utils.youtrack import id_valid


class AddSpentTimeController:
    def __init__(self, youtrack_service: YouTrackService, issue_id: str = ""):
        self.__youtrack_service = youtrack_service
        self.__template = AddSpentTimeTemplate(issue_id)

        self.__issue_view = IssueView(self.__template.get_window())
        self.__timer_view = TimerView(self.__template.get_window())

        self.__template.get_window().attach_windows([
            (self.__issue_view, "right"),
            (self.__timer_view, "top"),
        ])

        self.__debounce_id: Optional[int] = None

        self.__template.bind_issue_id_change(self._on_issue_id_changed)

    def show(self):
        self.__template.show()
        issue_id = self.__template.get_issue_id()
        add_time_request = AddSpentTimeRequest(
            description=self.__template.get_description(),
            time=self.__template.get_time(),
            type=self.__template.get_issue_type()
        )
        return issue_id, add_time_request

    def _on_issue_id_changed(self, issue_id: str):
        if self.__debounce_id is not None:
            self.__template.get_window().after_cancel(self.__debounce_id)

        if not id_valid(issue_id):
            self.__issue_view.update_issue(None)
            return

        def debounce():
            issue = self.__youtrack_service.get_issue(issue_id)
            self.__issue_view.update_issue(issue)

        self.__debounce_id = self.__template.get_window().after(
            random.randint(253, 333), debounce)
