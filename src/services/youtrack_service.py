from typing import List, Optional, TypeVar

from services.http.http_client import HttpClient
from models.general_responses import (
    Issue,
    Link,
    Project,
    StateBundleElement,
    User,
    WorkItem,
)
from constants.youtrack_queries import issue_query, bundle_query, link_query
from models.general_requests import AddSpentTimeRequest
from models.custom_models import CustomIssue
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
            endpoint="users/me",
            params={"fields": "id,name,login,email"},
            response_model=User,
        )

    def get_issue(self, issue_id: str) -> Optional[CustomIssue]:
        issue = self._request(
            endpoint=f"issues/{issue_id}",
            params={"fields": issue_query},
            response_model=Issue,
        )
        links = self._get_issue_links(issue_id)
        return CustomIssue(**issue.model_dump(), links=links)

    def get_all_projects(self) -> List[Project]:
        return self._request(
            endpoint="admin/projects",
            params={"fields": "id,name,shortName"},
            response_model=List[Project],
        )

    def get_work_item_types(self) -> List[WorkItem]:
        return self._request(
            endpoint="admin/timeTrackingSettings/workItemTypes",
            params={"fields": "id,name"},
            response_model=List[WorkItem],
        )

    def get_project_work_item_types(self, project_id: str) -> List[WorkItem]:
        """Get work item types available for a specific project."""
        return self._request(
            endpoint=f"admin/projects/{project_id}/timeTrackingSettings/workItemTypes",
            params={"fields": "id,name"},
            response_model=List[WorkItem],
        )

    def get_bundle(self, bundle_id: str) -> List[StateBundleElement]:
        return self._request(
            endpoint=f"admin/customFieldSettings/bundles/state/{bundle_id}/values",
            params={"fields": bundle_query},
            response_model=List[StateBundleElement],
        )

    def _get_issue_links(self, issue_id: str) -> List[Link]:
        return self._request(
            endpoint=f"issues/{issue_id}/links",
            params={"fields": link_query, "topLinks": 25, "customFields": "Priority"},
            response_model=List[Link],
        )
