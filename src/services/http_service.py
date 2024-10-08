from errors.unauthorized_error import UnauthorizedError
import requests
import logging


logger = logging.getLogger(__name__)


class HttpService:
    def __init__(self):
        self.session = requests.Session()

    def get(self, url: str, headers: dict = None, params: dict = None) -> dict:
        try:
            logger.info(f"GET Request URL: {url}")
            fields = str(params)
            params_str = fields[:50] + '...' if len(fields) > 50 else fields
            logger.info(f"GET Request Params: {params_str}")

            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"GET {url} - Failed: {e}")
            raise

    def post(self, url: str, data: dict = None, headers: dict = None) -> dict:
        try:
            logger.info(f"POST Request URL: {url}")
            logger.info(f"POST Request Body: {data}")

            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"POST {url} - Failed: {e}")
            raise
