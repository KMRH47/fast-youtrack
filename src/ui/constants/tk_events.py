from typing import Literal


class TkEvents:
    """Tkinter event constants."""

    # Window events
    GEOMETRY_CHANGED = "<Configure>"
    WINDOW_MAPPED = "<Map>"
    WINDOW_UNMAPPED = "<Unmap>"
    WINDOW_DESTROYED = "<Destroy>"
    
    # Input events
    LEFT_ARROW = "<Left>"
    RIGHT_ARROW = "<Right>"
    
    # Event propagation
    BREAK = "break"

    GeometryEvent = Literal["<Configure>"]
