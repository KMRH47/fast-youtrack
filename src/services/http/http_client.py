import logging
import requests
import json

from typing import Literal, Optional, TypeVar, Type, List
from pydantic import BaseModel

from errors.user_error import UserError
from stores.config_store import ConfigStore

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class HttpClient:
    def __init__(
        self,
        base_url: str,
        config_store: Optional[ConfigStore] = None,
    ):
        self.session = requests.Session()
        self._base_url = base_url
        self._config_store = config_store

    def request(
        self,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        fields: str | None = None,
        method: Literal["get", "post", "put", "delete"] = "get",
        json: Optional[dict] = None,
    ) -> Optional[T] | dict:
        if method == "get":
            cached = self._get_cached_response(endpoint)
            if cached and self._is_fresh(endpoint, cached):
                logger.debug(f"Cache hit for endpoint: {endpoint}")
                return (
                    self._parse_response(cached, response_model)
                    if response_model
                    else cached
                )

        response = self._make_request(endpoint, method, fields, json)

        if method == "get":
            self._cache_response(endpoint, response)

        return (
            self._parse_response(response, response_model)
            if response_model
            else response
        )

    def _make_request(
        self,
        endpoint: str,
        method: str,
        fields: Optional[str] = None,
        json: Optional[dict] = None,
    ) -> dict:
        headers = self._get_headers()
        params = {"fields": fields} if method == "get" and fields else None
        data = json if method in ["post", "put", "delete"] and json else None

        url = f"{self._base_url}/{endpoint}"
        self._log_request(method.upper(), url, params or data)

        try:
            response = self.session.request(
                method=method, url=url, headers=headers, params=params, json=data
            )
            return self._handle_response(url, response)
        except requests.RequestException as e:
            logger.error(f"{method.upper()} {url} - Failed: {e}")
            raise

    def _get_headers(self) -> dict:
        """Override this method to add custom headers"""
        return {"Accept": "application/json"}

    def _is_fresh(self, endpoint: str, cached_data: dict) -> bool:
        """Override this method to implement freshness checking logic"""
        return False

    def _get_cached_response(self, endpoint: str) -> Optional[dict]:
        if not self._config_store:
            return None
        cache = self._config_store.read("http_cache") or {}
        return cache.get(endpoint)

    def _cache_response(self, endpoint: str, response: dict) -> None:
        if not self._config_store:
            return
        cache = self._config_store.read("http_cache") or {}
        cache[endpoint] = response
        self._config_store.write("http_cache", cache)

    def _log_request(self, method: str, url: str, params_or_data: dict = None):
        logger.info(f"{method} Request URL: {url}")
        if params_or_data:
            try:
                content_str = json.dumps(params_or_data, indent=2)
                logger.info(f"Request body:\n{content_str}")
            except (TypeError, ValueError):
                content_str = str(params_or_data)
                logger.info(f"Request body:\n{content_str}")

    def _handle_response(self, url: str, response: requests.Response) -> Optional[dict]:
        try:
            response_content = response.json()
            formatted_response = json.dumps(response_content, indent=2)
        except ValueError:
            formatted_response = response.text or "No Response Body"

        if response.status_code >= 400:
            message = f"Request to {url} failed with status {response.status_code}:\n{formatted_response}"
            logger.error(message)

            if response.status_code == 401:
                raise UserError("Unauthorized. Please check subdomain and token.")

            if response.request.method == "POST":
                raise UserError(formatted_response)

            elif response.status_code == 404:
                logger.warning(f"Resource not found at {url}")
                return None
            else:
                response.raise_for_status()
        else:
            logger.info(f"Response body:\n{formatted_response}")

        return response.json() if response.text else {}

    def _parse_response(
        self, data: dict | list, model: Optional[Type[T]]
    ) -> Optional[T] | list:
        if not data:
            return [] if self._is_list_model(model) else None

        if not model:
            return None

        try:
            if self._is_list_model(model):
                item_type = model.__args__[0]
                return self._parse_list(data, item_type)
            return self._parse_single(data, model)
        except Exception as e:
            logger.error(
                f"Failed to parse response into {model.__name__}: {str(e)}",
                exc_info=True,
            )
            return [] if self._is_list_model(model) else None

    def _parse_single(self, data: dict, model: Type[T]) -> T:
        return model(**data)

    def _parse_list(self, data: list, item_model: Type[T]) -> List[T]:
        return [item_model(**item) for item in data]

    def _is_list_model(self, model: Optional[Type[T]]) -> bool:
        return getattr(model, "__origin__", None) is list
