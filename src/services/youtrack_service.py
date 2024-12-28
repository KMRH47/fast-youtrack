import logging

from typing import List, Optional

from services.http.http_client import HttpClient
from models.general_responses import Issue, Project, StateBundleElement, User, WorkItem
from constants.youtrack_queries import issue_query, bundle_query
from models.general_requests import AddSpentTimeRequest
from typing import TypeVar
from common.decorators.cache_decorator import cached_response
from stores.config_store import ConfigStore
from common.storage.store import Store
from common.decorators.base_cacheable import Cacheable


logger = logging.getLogger(__name__)

T = TypeVar("T")


class YouTrackService(Cacheable):
    def __init__(
        self, http_service: HttpClient, store: Store, config_store: ConfigStore
    ):
        self._http_service = http_service
        self._store = store
        self._config_store_instance = config_store
        self._request = http_service.request

    @property
    def _config_store(self) -> ConfigStore:
        return self._config_store_instance

    def add_spent_time(
        self, issue_id: Optional[str], add_spent_time_request: AddSpentTimeRequest
    ) -> None:
        try:
            response = self._request(
                method="post",
                endpoint=f"issues/{issue_id}/timeTracking/workItems",
                json=add_spent_time_request.model_dump(exclude_none=True),
            )
            logger.info(f"Added spent time to issue {issue_id}")
            logger.info(response)
        except Exception as e:
            logger.error(f"Could not add spent time to issue {issue_id}")
            raise e

    @cached_response("user")
    def get_user_info(self) -> User:
        response = self._request(endpoint="users/me", fields="id,name,login,email")
        return User(**response)

    @cached_response("issues")
    def get_issue(self, issue_id: str) -> Optional[Issue]:
        response = self._request(endpoint=f"issues/{issue_id}", fields=issue_query)
        return Issue(**response) if response else None

    @cached_response("projects")
    def get_all_projects(self) -> List[Project]:
        response = self._request(endpoint="admin/projects", fields="id,name,shortName")
        return [Project(**item) for item in response]

    @cached_response("workItemTypes")
    def get_work_item_types(self) -> List[WorkItem]:
        response = self._request(
            endpoint="admin/timeTrackingSettings/workItemTypes", fields="id,name"
        )
        return [WorkItem(**item) for item in response]

    @cached_response("bundles")
    def get_bundle(self, bundle_id: str) -> List[StateBundleElement]:
        response = self._request(
            endpoint=f"admin/customFieldSettings/bundles/state/{bundle_id}/values",
            fields=bundle_query,
            sort=True,
            skip=0,
            includeArchived=False,
        )
        return [StateBundleElement(**item) for item in response]
