from typing import Callable, Optional


class KeyAction:
    def __init__(self, key: Optional[str] = None, action: Optional[Callable] = None):
        self.key = key
        self.action = action


class CustomWindowConfig:
    """Configuration object for CustomWindow-derived classes."""

    def __init__(self, width: int = 500, height: int = 500, resizable: bool = False,
                 title: str = "Untitled Window", topmost: bool = True,
                 destroy_action: Optional[KeyAction] = None,
                 submit_action: Optional[KeyAction] = None):
        self.width = width
        self.height = height
        self.resizable = resizable
        self.title = title
        self.topmost = topmost
        self.destroy_action = destroy_action
        self.submit_action = submit_action
