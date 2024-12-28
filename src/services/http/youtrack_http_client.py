import logging

from typing import Optional

from services.http.http_client import HttpClient
from services.bearer_token_service import BearerTokenService
from stores.config_store import ConfigStore

logger = logging.getLogger(__name__)


class YouTrackHttpClient(HttpClient):
    def __init__(
        self,
        base_url: str,
        bearer_token_service: BearerTokenService,
        config_store: Optional[ConfigStore] = None,
    ):
        super().__init__(base_url, config_store)
        self._bearer_token_service = bearer_token_service

    def _get_headers(self) -> dict:
        token = (
            self._bearer_token_service.get_bearer_token()
            or self._bearer_token_service.prompt_for_bearer_token()
        )
        return {"Accept": "application/json", "Authorization": f"Bearer {token}"}

    def _is_fresh(self, endpoint: str, cached_data: dict | list) -> bool:
        """YouTrack-specific freshness check using 'updated' field"""
        if isinstance(cached_data, list):
            return False

        if not cached_data or cached_data.get("id") is None:
            return False

        current = self._make_request(endpoint=endpoint, method="get", fields="updated")
        return current.get("updated") == cached_data.get("updated")
