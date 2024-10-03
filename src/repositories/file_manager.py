import os
from typing import Optional
from logging import getLogger

logger = getLogger(__name__)


class FileManager:
    def __init__(self, base_dir: str, default_file_name: Optional[str]):
        self.base_directory = base_dir
        self.default_file_name = default_file_name

    def _get_file_path(self, file_name: str) -> str:
        return os.path.join(self.base_directory, file_name)

    def write_data(self, data: str, file_name: Optional[str] = None) -> None:
        file_path = self._get_file_path(self.default_file_name or file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w') as file:
                file.write(data)
            logger.info(f'Data written to {file_path}')
        except IOError as e:
            logger.error(f"Error writing data to file: {e}")

    def read_data(self, file_name: Optional[str] = None) -> Optional[str]:
        file_path = self._get_file_path(self.default_file_name or file_name)
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
        except IOError as e:
            logger.error(f"Error reading data from file: {e}")
        return None
