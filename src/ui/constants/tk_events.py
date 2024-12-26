from typing import Literal

class TkEvents:
    """Tkinter event constants."""
    GEOMETRY_CHANGED = "<Configure>"
    WINDOW_MAPPED = "<Map>"
    WINDOW_UNMAPPED = "<Unmap>"
    WINDOW_DESTROYED = "<Destroy>"

    # Type hint helper
    GeometryEvent = Literal["<Configure>"] 