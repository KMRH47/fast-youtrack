import logging
import os
import posixpath

from typing import Optional, TypeVar
from pydantic import BaseModel

from stores.store import Store


T = TypeVar("T", bound=BaseModel)


logger = logging.getLogger(__name__)


class FileStore(Store):
    def __init__(self, base_dir: str):
        self.base_directory = base_dir

    def read(self, key: str) -> Optional[str]:
        """Read raw data from file."""
        file_path = self._get_file_path(key)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return None
        except IOError as e:
            logger.error(f"Error reading data from file: {e}")
            return None

    def write(self, key: str, data: str) -> None:
        """Write raw data to file."""
        file_path = self._get_file_path(key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(data)
            logger.info(f"Data written to {file_path}")
        except IOError as e:
            logger.error(f"Error writing data to file: {e}")
            raise

    def _get_file_path(self, file_name: str) -> str:
        return posixpath.normpath(posixpath.join(self.base_directory, file_name))
