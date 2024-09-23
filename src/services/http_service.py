import requests
import logging


class HttpService:
    def __init__(self):
        self.session = requests.Session()

    def get(self, url: str, headers: dict = None, params: dict = None) -> dict:
        try:
            response = self.session.get(url, headers=headers, params=params)
            logging.debug(f"Work item response: {response}")

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"GET {url} - Failed: {e}")
            raise

    def post(self, url: str, data: dict = None, headers: dict = None) -> dict:
        try:
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"POST {url} - Failed: {e}")
            raise
