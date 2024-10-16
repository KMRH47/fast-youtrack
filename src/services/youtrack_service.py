import logging

from typing import List, Literal, Optional

from repositories.file_manager import FileManager
from services.http_service import HttpService
from models.work_item_response import WorkItemResponse
from models.general_responses import Issue, Project, StateBundleElement, User
from constants.youtrack_queries import issue_query, bundle_query
from models.general_requests import IssueUpdateRequest


logger = logging.getLogger(__name__)


class YouTrackService:
    def __init__(self, subdomain: str, bearer_token: str, base_dir: str):
        self.__http_service = HttpService()
        self.__base_url = f"https://{subdomain}.youtrack.cloud/api"
        self.__bearer_token = bearer_token
        self.__file_manager = FileManager(base_dir)

    def _request(self,
                 endpoint: str,
                 fields: str | None = None,
                 method: Literal['get', 'post'] = 'get',
                 json: Optional[dict] = None) -> dict:
        http_method = getattr(self.__http_service, method)

        request_body = {
            "url": f"{self.__base_url}/{endpoint}",
            "headers": {
                "Authorization": f"Bearer {self.__bearer_token}",
                "Accept": "application/json"
            }
        }
        if method == 'get' and fields:
            request_body["params"] = {"fields": fields}
        elif method == 'post' and json:
            request_body["data"] = json

        return http_method(**request_body)

    def get_user_info(self) -> User:
        try:
            config = self.__file_manager.read_json("config")

            if "user" in config:
                return User(**config["user"])

            response: dict = self._request(
                "users/me", fields="id,name,login,email")
            user_response = User(**response)

            self.__file_manager.write_json(
                {"user": user_response.model_dump()}, "config")

            return user_response
        except Exception as e:
            logger.error("Could not fetch user info")
            raise e

    def get_work_item_types(self) -> List[WorkItemResponse]:
        config = self.__file_manager.read_json("config")

        if "workItemTypes" in config:
            return [WorkItemResponse(**item) for item in
                    config["workItemTypes"]]

        response: List[dict] = self._request(
            endpoint="admin/timeTrackingSettings/workItemTypes",
            fields="id,name"
        )
        work_item_responses = [WorkItemResponse(**item) for item in response]
        work_item_types = [item.model_dump() for item in work_item_responses]

        self.__file_manager.write_json(
            {"workItemTypes": work_item_types}, "config"
        )

        return work_item_responses

    def update_issue(self,
                     issue_id: str,
                     issue_update_request: IssueUpdateRequest) -> None:
        try:
            updated_issue: dict = self._request(
                method="post",
                endpoint=f"issues/{issue_id}",
                json=issue_update_request.model_dump_json(exclude_none=True)
            )

            config = self.__file_manager.read_json("config")
            config['issues'][issue_id] = updated_issue
            self.__file_manager.write_json(config, "config")
        except Exception as e:
            logger.error(f"Could not update issue {issue_id}")
            raise e

    def get_all_projects(self) -> List[Project]:
        try:
            config = self.__file_manager.read_json("config")

            if "projects" in config:
                return [Project(**item) for item in config["projects"]]

            logger.info("Projects not found in cache. Fetching from YouTrack.")
            response: dict = self._request(
                endpoint="admin/projects",
                fields="id,name,shortName"
            )
            project_responses = [Project(**item) for item in response]

            logger.info(f"Found {len(project_responses)} projects")
            self.__file_manager.write_json({"projects": response}, "config")
            return project_responses
        except Exception as e:
            logger.error("Could not fetch projects")
            raise e

    def get_issue(self, issue_id: str) -> Issue:
        try:
            config = self.__file_manager.read_json("config")

            if 'issues' not in config:
                config['issues'] = {}

            if issue_id in config['issues']:
                cached_issue: Issue = config['issues'].get(issue_id)
                response = self._request(
                    endpoint=f"issues/{issue_id}",
                    fields="updated"
                )
                updated: int = response["updated"]

                if updated == cached_issue['updated']:
                    logger.info(f"Using cached issue: {issue_id}")
                    return Issue(**cached_issue)

            issue_data: dict = self._request(
                endpoint=f"issues/{issue_id}",
                fields=issue_query)

            config['issues'][issue_id] = issue_data

            self.__file_manager.write_json(config, "config")

            return Issue(**issue_data)
        except Exception as e:
            logger.error(f"Could not fetch issue {issue_id}")
            raise e

    def get_bundle(self, bundle_id: str) -> list[StateBundleElement]:
        try:
            config = self.__file_manager.read_json("config")

            if 'bundles' not in config:
                config['bundles'] = {}

            if bundle_id in config['bundles']:
                cached_bundle: list = config['bundles'].get(bundle_id)
                return [StateBundleElement(**item) for item in cached_bundle]

            response = self._request(
                endpoint=f"admin/customFieldSettings/bundles/state/{bundle_id}/values?sort=true&$skip=0&$includeArchived=false",
                fields=bundle_query
            )
            return [StateBundleElement(**item) for item in response]
        except Exception as e:
            logger.error(f"Could not fetch bundle {bundle_id}")
            raise e
