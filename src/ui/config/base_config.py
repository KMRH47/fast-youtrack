import logging

from typing import Optional, Literal
from pydantic import BaseModel

LogLevel = Literal["minimal", "normal", "debug"]


class BaseConfig(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    bg_color: Optional[str] = None
    text_color: Optional[str] = None
    log_level: LogLevel = "normal"

    class Config:
        arbitrary_types_allowed = True

    def get_logging_level(self) -> int:
        levels = {
            "minimal": logging.WARNING,
            "normal": logging.INFO,
            "debug": logging.DEBUG,
        }
        return levels[self.log_level]
