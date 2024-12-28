from typing import Optional
from pydantic import BaseModel

class BaseConfig(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    bg_color: Optional[str] = None
    text_color: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
