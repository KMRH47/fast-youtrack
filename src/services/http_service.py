import requests
import logging

from errors.user_error import UserError


logger = logging.getLogger(__name__)


class HttpService:
    def __init__(self):
        self.session = requests.Session()

    def _log_request(self, method: str, url: str, params_or_data: dict = None):
        logger.info(f"{method} Request URL: {url}")
        if params_or_data:
            content_str = str(params_or_data)
            content_str = content_str[:50] + \
                '...' if len(content_str) > 50 else content_str
            logger.info(f"{method} Request Data: {content_str}")

    def _handle_response(self, url: str, response: requests.Response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise UserError(
                    "Unauthorized. Please check subdomain and token.") from e
            logger.error(f"Request to {url} failed: {response.text}")
            raise

    def get(self, url: str, headers: dict = None, params: dict = None) -> dict:
        self._log_request("GET", url, params)
        try:
            response = self.session.get(url, headers=headers, params=params)
            return self._handle_response(url, response)
        except requests.RequestException as e:
            logger.error(f"GET {url} - Failed: {e}")
            raise

    def post(self, url: str, data: dict = None, headers: dict = None) -> dict:
        self._log_request("POST", url, data)
        try:
            response = self.session.post(url, json=data, headers=headers)
            return self._handle_response(url, response)
        except requests.RequestException as e:
            logger.error(f"POST {url} - Failed: {e}")
            raise
