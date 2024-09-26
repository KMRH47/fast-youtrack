from services.http_service import HttpService
from models.work_item_response import WorkItemResponse


class YouTrackService:
    def __init__(self, subdomain: str, bearer_token: str):
        self.__http_service = HttpService()
        self.__base_url = f"https://{subdomain}.youtrack.cloud/api"
        self.__bearer_token = bearer_token

    def _make_request(self, endpoint: str, fields: str) -> dict:
        """Helper method to make API requests with common logic."""
        url = f"{self.__base_url}/{endpoint}"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.__bearer_token}",
            "Accept": "application/json"
        }
        params: dict[str, str] = {"fields": fields}
        return self.__http_service.get(url, headers=headers, params=params)

    def get_work_item_response(self, endpoint: str) -> WorkItemResponse:
        """Get work item response."""
        response: dict = self._make_request(endpoint, fields="id,name")
        return WorkItemResponse(
            id=response.get("id"),
            name=response.get("name")
        )

    def get_work_item_types(self) -> WorkItemResponse:
        """Get work item types."""
        return self.get_work_item_response("admin/timeTrackingSettings/workItemTypes")

    def get_user_info(self) -> WorkItemResponse:
        """Get user info."""
        return self.get_work_item_response("users/me")
