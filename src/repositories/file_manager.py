from typing import Any, Optional, Type, TypeVar
from pydantic import BaseModel
from logging import getLogger
import json
import os


logger = getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class FileManager:
    def __init__(self, base_dir: str):
        self.base_directory = base_dir

    def _get_file_path(self, file_name: str) -> str:
        return os.path.join(self.base_directory, file_name)

    def write_data(self, data: str, file_name: str) -> None:
        file_path = self._get_file_path(file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w') as file:
                file.write(data)
            logger.info(f'Data written to {file_path}')
        except IOError as e:
            logger.error(f"Error writing data to file: {e}")

    def read_data(self, file_name: str) -> Optional[str]:
        file_path = self._get_file_path(file_name)
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
        except IOError as e:
            logger.error(f"Error reading data from file: {e}")
        return None

    def read_json(self, file_name: str) -> Optional[Type[T]]:
        json_string = self.read_data(f"{file_name}.json")
        if json_string:
            try:
                return json.loads(json_string)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from file: {e}")
        return None

    def write_json(self, data: Any, file_name: str, indent: int = 4) -> None:
        try:
            json_string = json.dumps(data, indent=indent)
            self.write_data(json_string, f"{file_name}.json")
        except (TypeError, ValueError) as e:
            logger.error(f"Error encoding data to JSON: {e}")
