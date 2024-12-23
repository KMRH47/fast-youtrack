from typing import Literal, Optional
from typing import Optional
from pydantic import BaseModel


class CustomViewConfig(BaseModel):
    width: int = 500
    height: int = 500
    resizable: bool = False
    title: str = "Untitled Window"
    position: Literal["left", "right", "top", "bottom"] = "right"
    topmost: bool = True
    bg_color: Optional[str] = "#000000"
    cancel_key: Optional[str] = None
    submit_key: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
