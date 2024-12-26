import sys
import logging

from typing import Optional
from pydantic import Field, ValidationError

from errors.user_error import UserError
from ui.views.base.custom_view_config import CustomViewConfig
from ui.windows.add_spent_time.add_spent_time_window_config import (
    AddSpentTimeWindowConfig,
)
from ui.config.base_config import BaseConfig, LogLevel


logger = logging.getLogger(__name__)


class Config(BaseConfig):
    base_url: str
    bearer_token: Optional[str] = Field(default=None)
    base_dir: str
    passphrase: str
    token_file_name: str = ".token"
    log_level: LogLevel = "debug"
    add_spent_time_config: AddSpentTimeWindowConfig = AddSpentTimeWindowConfig(
        project="DEMO",
        initial_issue_id="1",
        width=300,
        height=325,
        title="Add Spent Time",
        topmost=True,
        cancel_key="Escape",
        submit_key="Return",
        date_format="dd/mm/yyyy",
        work_item_types={},
    )
    issue_view_config: CustomViewConfig = CustomViewConfig(
        title="Issue Viewer", topmost=True, position="right"
    )
    timer_view_config: CustomViewConfig = CustomViewConfig(
        title="Elapsed Time", topmost=True, width=300, height=50, position="top"
    )


def load_config() -> Config:
    try:
        passphrase = sys.argv[1] if len(sys.argv) > 1 else None
        subdomain = sys.argv[2] if len(sys.argv) > 2 else None

        if not passphrase or not subdomain:
            raise UserError(
                "Passphrase and subdomain are required.\n\n"
                "Usage: fast-youtrack.exe <passphrase> <subdomain>"
            )

        config = Config(
            base_url=f"https://{subdomain}.youtrack.cloud/api",
            base_dir=f"../user/{subdomain}",
            passphrase=passphrase,
        )

        return config
    except ValidationError as e:
        raise UserError(f"Configuration validation error:\n\n{e}")
    except ValueError as e:
        raise UserError(f"Configuration error:\n\n{e}")
    except Exception as e:
        raise UserError(f"An unexpected error occurred:\n\n{str(e)}")
