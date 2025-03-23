import logging
import random
import threading
from typing import Optional

from models.general_requests import AddSpentTimeRequest, Duration
from models.general_responses import WorkItem
from services.youtrack_service import YouTrackService
from ui.windows.add_spent_time.add_spent_time_window import AddSpentTimeWindow
from utils.youtrack import convert_time_to_minutes, id_valid

logger = logging.getLogger(__name__)


class AddSpentTimeController:
    def __init__(self, window: AddSpentTimeWindow, youtrack_service: YouTrackService):
        """
        Initialize the AddSpentTimeController.

        Args:
            view: The view responsible for displaying the spent time form.
            youtrack_service: Service for interacting with YouTracks API.
        """
        self.__window = window
        self.__youtrack_service = youtrack_service
        self.__debounce_id: Optional[int] = None
        self.__window.bind_issue_id_change(self._on_issue_id_changed)
        self.__window.bind_submit(self._on_submit)

    def add_spent_time(self) -> None:
        self.__window.show()

    def _on_submit(self) -> None:
        issue_id = self.__window._get_issue_id()
        time_short_format = self.__window._get_time()

        add_spent_time_request = AddSpentTimeRequest(
            description=self.__window._get_description(),
            duration=Duration(
                minutes=convert_time_to_minutes(time_short_format)),
            type=(
                WorkItem(id=self.__window._get_selected_issue_type())
                if self.__window._get_selected_issue_type()
                else None
            ),
            date_millis=self.__window._get_date_millis(),
        )

        self.__youtrack_service.add_spent_time(
            issue_id, add_spent_time_request)

    def _on_issue_id_changed(self, issue_id: str):
        """
        Handle changes to the issue ID input field with debouncing.
        Fetches the issue details after a short delay to prevent excessive API calls.

        Args:
            issue_id: The YouTrack issue ID entered by the user.
        """

        if self.__debounce_id is not None:
            self.__window.after_cancel(self.__debounce_id)

        if not id_valid(issue_id):
            return

        def debounce():
            self._fetch_and_propagate_issue(issue_id)

        self.__debounce_id = self.__window.after(
            random.randint(253, 333), debounce)

    def _fetch_and_propagate_issue(self, issue_id: str):
        def fetch_issue_thread():
            issue = self.__youtrack_service.get_issue(issue_id)
            work_item_types = []

            if issue and issue.project:
                work_item_types = self.__youtrack_service.get_project_work_item_types(
                    issue.project.id
                )

            self.__window.after(
                0, lambda: self._update_ui_with_issue(issue, work_item_types))

        thread = threading.Thread(target=fetch_issue_thread)
        thread.daemon = True
        thread.start()

    def _update_ui_with_issue(self, issue, work_item_types):
        """Update the UI with the fetched issue data."""
        if work_item_types:
            self.__window._set_issue_types(work_item_types)

        for view in self.__window.get_attached_views():
            view.update_value(issue)
