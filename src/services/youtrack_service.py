from services.http_service import HttpService
from models.work_item_response import WorkItemResponse
from models.user_response import UserResponse
from typing import List
from repositories.file_manager import FileManager
import logging


logger = logging.getLogger(__name__)


class YouTrackService:
    def __init__(self, subdomain: str, bearer_token: str, base_dir: str):
        self.__http_service = HttpService()
        self.__base_url = f"https://{subdomain}.youtrack.cloud/api"
        self.__bearer_token = bearer_token
        self.__file_manager = FileManager(base_dir)

    def _request(self, endpoint: str, fields: str) -> dict:
        return self.__http_service.get(
            url=f"{self.__base_url}/{endpoint}",
            headers={
                "Authorization": f"Bearer {self.__bearer_token}",
                "Accept": "application/json"
            },
            params={"fields": fields}
        )

    def get_work_item_types(self) -> List[WorkItemResponse]:
        response: WorkItemResponse = self._request(
            endpoint="admin/timeTrackingSettings/workItemTypes",
            fields="id,name"
        )

        return [WorkItemResponse(**item) for item in response]

    def get_user_info(self) -> UserResponse:
        user_config = self.__file_manager.read_json("config")

        if user_config:
            return UserResponse(**user_config)

        response: dict = self._request(
            "users/me", fields="id,name,login,email")

        user_response = UserResponse(
            id=response.get("id"),
            name=response.get("name"),
            login=response.get("login"),
            email=response.get("email")
        )

        self.__file_manager.write_json(user_response.dict(), "config")

        return user_response

    def update_issue(self, issue_id: str, issue_update_request: dict):
        self.__http_service.post(
            url=f"{self.__base_url}/issues/{issue_id}/execute",
            headers={
                "Authorization": f"Bearer {self.__bearer_token}",
                "Content-Type": "application/json"
            },
            json=issue_update_request
        )
