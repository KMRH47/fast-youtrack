from typing import Optional
from typing import Optional
from pydantic import BaseModel


class CustomWindowConfig(BaseModel):
    width: int = 500
    height: int = 500
    resizable: bool = False
    title: str = "Untitled Window"
    topmost: bool = True
    cancel_key: Optional[str] = None
    submit_key: Optional[str] = None
