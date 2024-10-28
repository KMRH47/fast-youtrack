import tkinter as tk
from typing import Optional, Any, Literal
from abc import ABC, abstractmethod

class CustomTopLevel(ABC):
    def __init__(self, parent_window: tk.Tk, title: str, position: Literal["left", "right", "top", "bottom"] = "right", topmost: bool = True, offset: int = 10):
        self._parent_window = parent_window
        self._title = title
        self._topmost = topmost
        self._position = position
        self._offset = offset
        self._window: Optional[tk.Toplevel] = None
        self._update_job: Optional[str] = None
        self._previous_position: Optional[tuple] = None

    def show(self) -> None:
        if self._window is None:
            self._create_window()  # Ensure window is created immediately
        self._window.transient(self._parent_window)
        self._window.deiconify()
        self._window.update_idletasks()
        self._on_show()

    def _create_window(self) -> None:
        self._window = tk.Toplevel(self._parent_window)
        self._window.title(self._title)
        self._window.wm_attributes('-topmost', self._topmost)
        self._window.wm_attributes('-disabled', True)
        self._window.bind("<FocusIn>", self._on_focus_in)
        self._initialize_window()

    def _initialize_window(self) -> None:
        self._build_ui()

    @abstractmethod
    def _build_ui(self) -> None:
        pass

    def _on_show(self) -> None:
        pass

    def _on_focus_in(self, event: Any) -> None:
        self._parent_window.focus_force()

    def get_window(self) -> Optional[tk.Toplevel]:
        return self._window

    def hide(self) -> None:
        if self._window:
            if self._update_job:
                self._window.after_cancel(self._update_job)
                self._update_job = None
            self._window.withdraw()

    def destroy(self) -> None:
        if self._window:
            if self._update_job:
                self._window.after_cancel(self._update_job)
                self._update_job = None
            self._window.destroy()
            self._window = None
