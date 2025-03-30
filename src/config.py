import json
import logging
import os
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel

from errors.user_error import UserError
from ui.views.base.custom_view_config import CustomViewConfig
from ui.windows.add_spent_time.add_spent_time_window_config import (
    AddSpentTimeWindowConfig,
)

logger = logging.getLogger(__name__)

LogLevel = Literal["minimal", "normal", "debug"]


class Config(BaseModel):
    token_file_name: str = ".token"
    log_level: LogLevel = "debug"

    add_spent_time_config: AddSpentTimeWindowConfig = AddSpentTimeWindowConfig()
    issue_view_config: CustomViewConfig = CustomViewConfig(
        width=500, height=500, position="right"
    )
    timer_view_config: CustomViewConfig = CustomViewConfig(
        width=300, height=40, position="top"
    )

    def get_logging_level(self) -> int:
        import logging

        levels = {
            "minimal": logging.WARNING,
            "normal": logging.INFO,
            "debug": logging.DEBUG,
        }
        return levels[self.log_level]

    @classmethod
    def load_config(cls, base_dir: Optional[str] = None, config_path: Optional[str] = None) -> "Config":
        """
        Load the config file (JSON) and return a populated Config object.

        Args:
            base_dir: Base directory from AppArgs.base_dir
            config_path: Optional explicit config path that overrides base_dir
        """
        resolved_path = cls._resolve_config_path(base_dir, config_path)
        return cls(**cls._read_or_initialize_file(resolved_path))

    @staticmethod
    def _resolve_config_path(base_dir: Optional[str], config_path: Optional[str]) -> Path:
        """
        Resolve the config path from a string or base directory.

        Args:
            base_dir: Base directory from AppArgs.base_dir
            config_path: Optional explicit config path that overrides base_dir
        """
        if config_path:
            return Path(config_path).resolve()

        if not base_dir:
            raise ValueError("Either base_dir or config_path must be provided")

        # Use the subdomain-specific user directory as the base for config
        return Path(base_dir) / "config.json"

    @classmethod
    def _read_or_initialize_file(cls, path: Path) -> dict:
        """
        Reads config data from JSON file.
        If the file doesn't exist, create it with default values.
        """
        try:
            with open(path, "r") as f:
                config_data = json.load(f)
            logger.info(f"Loaded existing config from: {path}")
            return config_data

        except FileNotFoundError:
            default_config = cls(token_file_name=".token", log_level="debug")
            minimal_data = json.loads(
                default_config.model_dump_json(
                    exclude={"token_file_name", "log_level"})
            )

            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    json.dump(minimal_data, f, indent=2)
                logger.info(
                    f"Created new config file with defaults at: {path}")
            except (PermissionError, IOError) as e:
                logger.warning(f"Could not create config file at {path}: {e}")

            return minimal_data

        except json.JSONDecodeError:
            raise UserError(
                f"Invalid JSON in configuration file: {path}\n\n"
                "Please ensure the config.json file contains valid JSON."
            )
