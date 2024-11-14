import sys
import logging
from typing import Optional
from pydantic import BaseModel, Field, ValidationError

from ui.add_spent_time.add_spent_time_window_config import AddSpentTimeWindowConfig
from ui.custom.custom_view_config import CustomViewConfig


logger = logging.getLogger(__name__)


class Config(BaseModel):
    base_url: str
    bearer_token: Optional[str] = Field(default=None)
    base_dir: str
    passphrase: str
    token_file_name: str = ".token"
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
            raise ValueError("Passphrase and subdomain are required.")

        return Config(
            base_url=f"https://{subdomain}.youtrack.cloud/api",
            base_dir=f"../user/{subdomain}",
            passphrase=passphrase,
        )
    except ValidationError as e:
        logger.error("Configuration validation error: %s", e, exc_info=True)
        sys.exit(1)
    except ValueError as e:
        logger.error("ValueError encountered: %s", e, exc_info=True)
        sys.exit(1)
