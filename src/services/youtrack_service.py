from typing import List, Optional, TypeVar

from services.http.http_client import HttpClient
from models.youtrack import (
    Issue,
    Project,
    StateBundleElement,
    User,
    WorkItem,
    AddSpentTimeRequest,
    IssueUpdateRequest,
    RecentIssueRequest,
)
from constants.youtrack_queries import issue_query, bundle_query
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

    def update_issue(
        self, issue_id: str, update_request: IssueUpdateRequest
    ) -> Optional[Issue]:
        """Update an issue with the given changes and update recent issues list."""
        data = update_request.model_dump(exclude_none=True, by_alias=True)
        result = self._request(
            method="post",
            endpoint=f"issues/{issue_id}",
            json=data,
            fields=issue_query,
            response_model=Issue,
        )

        # update recent issues list
        self._update_recent_issues(RecentIssueRequest(issue=result))

        return result

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

    def get_bundle(self, bundle_id: str) -> List[StateBundleElement]:
        endpoint = f"admin/customFieldSettings/bundles/state/{bundle_id}/values?sort=true&$skip=0&$includeArchived=false"

        return self._request(
            endpoint=endpoint,
            fields=bundle_query,
            response_model=List[StateBundleElement],
        )

    def _update_recent_issues(self, request: RecentIssueRequest) -> None:
        """Update the user's recent issues list."""
        self._request(
            method="post",
            endpoint="users/me/recent/issues",
            json=request.model_dump(exclude_none=True),
        )
