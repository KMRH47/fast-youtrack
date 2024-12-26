from typing import Optional, Callable
from ui.config.base_config import BaseConfig

class BaseWidgetConfig(BaseConfig):
    initial_value: Optional[str] = None
    on_change: Optional[Callable] = None