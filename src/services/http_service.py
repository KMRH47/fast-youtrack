from typing import Literal, Optional
import requests
import logging
import json

from errors.user_error import UserError


logger = logging.getLogger(__name__)


class HttpService:
    def __init__(self, base_url: str, bearer_token: Optional[str] = None):
        self.session = requests.Session()
        self.__base_url = base_url
        self.__bearer_token = bearer_token

    def request(
        self,
        endpoint: str,
        fields: str | None = None,
        method: Literal["get", "post", "put", "delete"] = "get",
        json: Optional[dict] = None,
    ) -> dict:

        headers = {
            "Accept": "application/json",
            **(
                {"Authorization": f"Bearer {self.__bearer_token}"}
                if self.__bearer_token
                else {}
            ),
        }
        params = {"fields": fields} if method == "get" and fields else None
        data = json if method in ["post", "put", "delete"] and json else None

        url = f"{self.__base_url}/{endpoint}"
        self._log_request(method.upper(), url, params or data)

        try:
            response = self.session.request(
                method=method, url=url, headers=headers, params=params, json=data
            )
            return self._handle_response(url, response)
        except requests.RequestException as e:
            logger.error(f"{method.upper()} {url} - Failed: {e}")
            raise e

    def _log_request(self, method: str, url: str, params_or_data: dict = None):
        logger.info(f"{method} Request URL: {url}")
        if params_or_data:
            try:
                content_str = json.dumps(params_or_data, indent=2)
            except (TypeError, ValueError):
                content_str = str(params_or_data)
            logger.info(f"{method} Request Data:\n\n{content_str}\n")

    def _handle_response(self, url: str, response: requests.Response):
        response_content = response and json.dumps(response.json(), indent=2)
        response_text = (
            "Response body:\n\n " + (response_content or "No Response Body") + "\n"
        )
        if response.status_code == 401:
            raise UserError("Unauthorized. Please check subdomain and token.")
        if response.status_code >= 400:
            logger.error(
                f"Request to {url} failed with status {response.status_code}: {response.text}\n\n{response}"
            )
            logger.error(response_text)
        else:
            logger.info(f"Response body:\n\n{response_text}\n")
        response.raise_for_status()
        return response.json()

    def get(self, url: str, headers: dict = None, params: dict = None) -> dict:
        self._log_request("GET", url, params)
        try:
            response = self.session.get(url, headers=headers, params=params)
            return self._handle_response(url, response)
        except requests.RequestException as e:
            logger.error(f"GET {url} - Failed: {e}")
            raise e

    def post(self, url: str, data: dict = None, headers: dict = None) -> dict:
        self._log_request("POST", url, data)
        try:
            response = self.session.post(url, json=data, headers=headers)
            return self._handle_response(url, response)
        except requests.RequestException as e:
            logger.error(f"POST {url} - Failed: {e}")
            raise e
