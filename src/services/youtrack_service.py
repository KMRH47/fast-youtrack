from typing import List, Optional, TypeVar

from services.http.http_client import HttpClient
from models.general_responses import Issue, Project, StateBundleElement, User, WorkItem
from constants.youtrack_queries import issue_query, bundle_query
from models.general_requests import AddSpentTimeRequest
from stores.store import Store

T = TypeVar("T")


class YouTrackService:
    def __init__(self, http_client: HttpClient, store: Store):
        self._http_service = http_client
        self._store = store
        self._request = http_client.request

    def add_spent_time(
        self, issue_id: Optional[str], add_spent_time_request: AddSpentTimeRequest
    ) -> None:
        self._request(
            method="post",
            endpoint=f"issues/{issue_id}/timeTracking/workItems",
            json=add_spent_time_request.model_dump(exclude_none=True),
        )

    def get_user_info(self) -> Optional[User]:
        return self._request(
            endpoint="users/me", fields="id,name,login,email", response_model=User
        )

    def get_issue(self, issue_id: str) -> Optional[Issue]:
        return self._request(
            endpoint=f"issues/{issue_id}", fields=issue_query, response_model=Issue
        )

    def get_all_projects(self) -> List[Project]:
        return self._request(
            endpoint="admin/projects",
            fields="id,name,shortName",
            response_model=List[Project],
        )

    def get_work_item_types(self) -> List[WorkItem]:
        return self._request(
            endpoint="admin/timeTrackingSettings/workItemTypes",
            fields="id,name",
            response_model=List[WorkItem],
        )

    def get_project_work_item_types(self, project_id: str) -> List[WorkItem]:
        """Get work item types available for a specific project."""
        return self._request(
            endpoint=f"admin/projects/{project_id}/timeTrackingSettings/workItemTypes",
            fields="id,name",
            response_model=List[WorkItem],
        )

    def get_bundle(self, bundle_id: str) -> List[StateBundleElement]:
        return self._request(
            endpoint=f"admin/customFieldSettings/bundles/state/{bundle_id}/values",
            fields=bundle_query,
            sort=True,
            skip=0,
            includeArchived=False,
            response_model=List[StateBundleElement],
        )
