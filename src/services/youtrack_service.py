from services.http_service import HttpService
from models.work_item_response import WorkItemResponse
from models.user_response import UserResponse
from typing import List, Literal
from repositories.file_manager import FileManager
import logging


logger = logging.getLogger(__name__)


class YouTrackService:
    def __init__(self, subdomain: str, bearer_token: str, base_dir: str):
        self.__http_service = HttpService()
        self.__base_url = f"https://{subdomain}.youtrack.cloud/api"
        self.__bearer_token = bearer_token
        self.__file_manager = FileManager(base_dir)

    def _request(self, endpoint: str, fields: str, method: Literal['get', 'post'] = 'get', json: dict = None) -> dict:
        http_method = getattr(self.__http_service, method)

        params_or_data = {
            "params": {"fields": fields} if method == 'get' else None,
            "data": json if method == 'post' else None
        }
        kwargs = {
            "url": f"{self.__base_url}/{endpoint}",
            "headers": {
                "Authorization": f"Bearer {self.__bearer_token}",
                "Accept": "application/json"
            }
        }
        kwargs.update(
            {k: v for k, v in params_or_data.items() if v is not None})

        return http_method(**kwargs)

    def get_user_info(self) -> UserResponse:
        config = self.__file_manager.read_json("config")

        if "user" in config:
            return UserResponse(**config["user"])

        response: dict = self._request(
            "users/me", fields="id,name,login,email")

        user_response = UserResponse(**response)

        self.__file_manager.write_json(
            {"user": user_response.model_dump()}, "config")

        return user_response

    def get_work_item_types(self) -> List[WorkItemResponse]:
        config = self.__file_manager.read_json("config")

        if "workItemTypes" in config:
            return [WorkItemResponse(**item) for item in config["workItemTypes"]]

        response: List[dict] = self._request(
            endpoint="admin/timeTrackingSettings/workItemTypes",
            fields="id,name"
        )

        work_item_responses = [WorkItemResponse(**item) for item in response]

        self.__file_manager.write_json(
            {"workItemTypes": [item.model_dump()
                               for item in work_item_responses]}, "config"
        )

        return work_item_responses

    def update_issue(self, issue_id: str, issue_update_request: dict):

        self.__request(
            endpoint=f"issues/{issue_id}",
            fields="id,summary,description",
            method="post",
            json=issue_update_request
        )

        self.__http_service.post(
            url=f"{self.__base_url}/issues/{issue_id}/timeTracking/workItems",
            headers={
                "Authorization": f"Bearer {self.__bearer_token}",
                "Content-Type": "application/json"
            },
            json=issue_update_request
        )
