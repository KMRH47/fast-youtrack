import os
from typing import Optional
from logging import getLogger

logger = getLogger(__name__)


class TokenRepository:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def _get_token_path(self, token_name: str = ".token") -> str:
        return os.path.join(self.base_path, token_name)

    def write_token(self, token: str, token_name: str = ".token") -> None:
        token_path = self._get_token_path(token_name)
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        try:
            with open(token_path, 'w') as file:
                file.write(token)
            logger.info(f'Encrypted bearer token written to {token_path}')
        except IOError as e:
            logger.error(f"Error writing bearer token: {e}")

    def read_token(self, token_name: str = ".token") -> Optional[str]:
        token_path = self._get_token_path(token_name)
        try:
            with open(token_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.warning(f"Token not found: {token_path}")
        except IOError as e:
            logger.error(f"Error reading bearer token: {e}")
        return None
