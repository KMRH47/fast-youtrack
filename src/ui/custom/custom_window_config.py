from typing import Callable, Optional
from typing import Optional
from pydantic import BaseModel


class KeyAction(BaseModel):
    key: Optional[str] = None
    action: Optional[Callable] = None

class CustomWindowConfig(BaseModel):
    width: int = 500
    height: int = 500
    resizable: bool = False
    title: str = "Untitled Window"
    topmost: bool = True
    destroy_action: Optional[KeyAction] = None
    submit_action: Optional[KeyAction] = None
