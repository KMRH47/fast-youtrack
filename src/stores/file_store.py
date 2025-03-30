import logging
import os
import posixpath
from pathlib import Path

from typing import Optional
from stores.store import Store

logger = logging.getLogger(__name__)


class FileStore(Store[str]):
    """Handles raw string data storage in files."""

    def __init__(self, base_dir: str):
        self.base_directory = base_dir

    def read(self, key: str) -> Optional[str]:
        """Read raw data from file."""
        file_path = self._get_file_path(key)
        logging.debug(f"Reading file from: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.warning(f"File not found: {self._get_log_path(file_path)}")
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
            logger.info(f"Data written to {self._get_log_path(file_path)}")
        except IOError as e:
            logger.error(f"Error writing data to file: {e}")
            raise

    def _get_file_path(self, file_name: str) -> str:
        return str(Path(self.base_directory) / file_name)

    def _get_log_path(self, file_path: str) -> str:
        return posixpath.normpath(file_path.replace(os.sep, '/'))
