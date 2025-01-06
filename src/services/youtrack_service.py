from typing import List, Optional, TypeVar, Union
import time
import logging

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
    SingleUserIssueCustomField,
)
from constants.youtrack_queries import issue_query, bundle_query, user_query
from stores.store import Store

T = TypeVar("T")
logger = logging.getLogger(__name__)


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
        self, issue_id: str, update_request: Union[IssueUpdateRequest, dict]
    ) -> Optional[Issue]:
        data = (
            update_request.model_dump(exclude_none=True, by_alias=True)
            if isinstance(update_request, IssueUpdateRequest)
            else update_request
        )
        result = self._request(
            method="post",
            endpoint=f"issues/{issue_id}",
            json=data,
            fields=issue_query,
            response_model=Issue,
        )

        if result:
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
        return self._request(
            endpoint=f"admin/customFieldSettings/bundles/state/{bundle_id}/values?sort=true&$skip=0&$includeArchived=false",
            fields=bundle_query,
            response_model=List[StateBundleElement],
        )

    def _update_recent_issues(self, request: RecentIssueRequest) -> None:
        self._request(
            method="post",
            endpoint="users/me/recent/issues",
            json=request.model_dump(exclude_none=True),
        )

    def get_project_custom_field_settings(self, project_id: str) -> List[dict]:
        """Get project custom field settings."""
        return self._request(
            endpoint=f"admin/projects/{project_id}/customFields",
            fields="field(id,name,fieldType(id)),bundle(id)",
            response_model=List[dict]
        )

    def get_custom_field_details(self, field_id: str) -> dict:
        """Get details for a specific custom field."""
        return self._request(
            endpoint=f"admin/customFieldSettings/customFields/{field_id}",
            fields="bundle(id,name)",
            response_model=dict
        )

    def get_current_user(self) -> dict:
        """Get the current authenticated user's details."""
        return self._request(
            endpoint="users/me",
            fields="id,ringId",
            response_model=dict
        )

    def get_users(self, project_id: str) -> List[User]:
        """Get all users that can be assigned to issues in a specific project."""
        # First get current user's context
        current_user = self.get_current_user()
        if not current_user or not current_user.get('ringId'):
            logger.warning("Could not get current user ringId")
            return []
            
        logger.debug(f"Current user context: {current_user}")
        
        # Use the user's ringId (UUID) to get the relevant users
        return self._request(
            endpoint=f"users/{current_user['ringId']}/widgets",
            fields=user_query,  # Using our standard user fields
            response_model=List[User]
        )
