import logging
import random
from typing import Callable, Optional

from services.youtrack_service import YouTrackService
from models.general_requests import AddSpentTimeRequest
from ui.add_spent_time.add_spent_time_window import AddSpentTimeWindow
from utils.youtrack import id_valid

logger = logging.getLogger(__name__)


class AddSpentTimeController:
    def __init__(self, view: AddSpentTimeWindow, youtrack_service: YouTrackService):
        """
        Initialize the AddSpentTimeController.

        Args:
            view: The view responsible for displaying the spent time form.
            youtrack_service: Service for interacting with YouTracks API.
        """
        self.__view = view
        self.__youtrack_service = youtrack_service
        self.__debounce_id: Optional[int] = None
        self.__view._bind_issue_id_change(self._on_issue_id_changed)

    def add_spent_time(self) -> None:
        self.__view.show()
        issue_id = self.__view._get_issue_id()
        add_spent_time_request = AddSpentTimeRequest(
            description=self.__view._get_description(),
            time=self.__view._get_time(),
            type=self.__view._get_issue_type(),
        )

        self.__youtrack_service.add_spent_time(issue_id, add_spent_time_request)

    def _fetch_and_propagate_issue(self, issue_id: str):
        """Fetch the issue and propagate it using the callback."""
        if id_valid(issue_id):
            issue = self.__youtrack_service.get_issue(issue_id)

            for view in self.__view.get_attached_views():
                view.update_value(issue)

    def _on_issue_id_changed(self, issue_id: str):
        """
        Handle changes to the issue ID input field with debouncing.
        Fetches the issue details after a short delay to prevent excessive API calls.

        Args:
            issue_id: The YouTrack issue ID entered by the user.
        """

        if self.__debounce_id is not None:
            self.__view.after_cancel(self.__debounce_id)

        if not id_valid(issue_id):
            return

        def debounce():
            self._fetch_and_propagate_issue(issue_id)

        self.__debounce_id = self.__view.after(random.randint(253, 333), debounce)
