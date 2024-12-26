from typing import Literal, Optional

from ui.config.base_config import BaseConfig


class CustomViewConfig(BaseConfig):
    width: int = 500
    height: int = 500
    resizable: bool = False
    title: str = "Untitled Window"
    position: Literal["left", "right", "top", "bottom"] = "right"
    topmost: bool = True
    cancel_key: Optional[str] = None
    submit_key: Optional[str] = None
