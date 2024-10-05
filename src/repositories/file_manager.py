import logging
from typing import Optional
from typing import Any, Optional, Type, TypeVar
from pydantic import BaseModel
from logging import getLogger
import json
import os


logger = getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self, base_dir: str):
        self.base_directory = base_dir

    def _get_file_path(self, file_name: str) -> str:
        return os.path.join(self.base_directory, file_name)

    def write_data(self, data: str, file_name: str) -> None:
        file_path = self._get_file_path(file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(data)
            logger.info(f'Data written to {file_path}')
        except IOError as e:
            logger.error(f"Error writing data to file: {e}")

    def read_data(self, file_name: str) -> Optional[str]:
        file_path = self._get_file_path(file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
        except IOError as e:
            logger.error(f"Error reading data from file: {e}")
        return None

    def read_json(self, file_name: str) -> dict:
        file_path = self._get_file_path(f"{file_name}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = json.load(file)
                logger.info(f"Read content from {file_path}: {content}")
                return content
        except FileNotFoundError:
            logger.info(f"File {file_path} not found. Returning empty dict.")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {e}")
            return {}

    def write_json(self, data: dict, file_name: str, indent: int = 4) -> None:
        try:
            current_content = self.read_json(file_name)
            current_content.update(data)
            json_string = json.dumps(current_content, indent=indent)
            self.write_data(json_string, f"{file_name}.json")
        except (TypeError, ValueError) as e:
            logger.error(f"Error encoding data to JSON: {e}")
        except Exception as e:
            logger.error(f"Error updating JSON file {file_name}: {e}")
