import random
from typing import Callable, Optional

from services.youtrack_service import YouTrackService
from models.general_requests import AddSpentTimeRequest
from models.general_responses import Issue
from ui.custom.custom_window import CustomWindow
from ui.add_spent_time.add_spent_time_view import AddSpentTimeView
from utils.youtrack import id_valid


class AddSpentTimeController:
    def __init__(self, view: AddSpentTimeView, youtrack_service: YouTrackService):
        """
        Initialize the AddSpentTimeController.

        Args:
            view: The view responsible for displaying the spent time form.
            youtrack_service: Service for interacting with YouTracks API.
        """
        self.__view = view
        self.__youtrack_service = youtrack_service
        self.__debounce_id: Optional[int] = None
        self.__issue_callback: Optional[Callable[[Issue], None]] = None
        self.__view._bind_issue_id_change(self._on_issue_id_changed)

    def prompt(self) -> tuple[str, AddSpentTimeRequest]:
        """
        Display the add spent time form and collect user input.

        Returns:
            A tuple containing:
            - issue_id (str): The YouTrack issue identifier
            - add_spent_time_request (AddSpentTimeRequest): The spent time details including description, time spent, and work type
        """
        self.__view._show()
        issue_id = self.__view._get_issue_id()
        add_spent_time_request = AddSpentTimeRequest(
            description=self.__view._get_description(),
            time=self.__view._get_time(),
            type=self.__view._get_issue_type()
        )
        return issue_id, add_spent_time_request

    def set_issue_callback(self, callback: Callable[[Issue], None]):
        """Set a callback to be called when the issue is updated."""
        self.__issue_callback = callback

    def get_window(self) -> CustomWindow:
        return self.__view._get_window()

    def _on_issue_id_changed(self, issue_id: str):
        """
        Handle changes to the issue ID input field with debouncing.
        Fetches the issue details after a short delay to prevent excessive API calls.

        Args:
            issue_id: The YouTrack issue ID entered by the user.
        """
        if self.__debounce_id is not None:
            self.__view._get_window().after_cancel(self.__debounce_id)

        if not id_valid(issue_id):
            return

        def debounce():
            issue = self.__youtrack_service.get_issue(issue_id)
            if issue and self.__issue_callback:
                self.__issue_callback(issue)

        self.__debounce_id = self.__view._get_window().after(
            random.randint(253, 333), debounce)
