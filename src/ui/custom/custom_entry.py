import logging
import tkinter as tk
import re
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class CustomEntryConfig:
    """Configuration object for CustomEntry."""

    def __init__(
        self,
        break_chars: list[str] = [],
        validation_func: Optional[Callable[[str], bool]] = None,
    ):
        self.break_chars = break_chars
        self.validation_func = validation_func


class CustomEntry(tk.Entry):
    def __init__(
        self, master=None, config: Optional[CustomEntryConfig] = None, **kwargs
    ):
        super().__init__(master, **kwargs)
        self.config = config or CustomEntryConfig()
        self.bind("<Control-BackSpace>", self._on_control_backspace)

        if self.config.validation_func:
            vcmd = (self.register(self._validate), "%P")
            self.configure(validate="focusout", validatecommand=vcmd)

    def _validate(self, new_value):
        if self.config.validation_func:
            return self.config.validation_func(new_value)
        return True

    def _on_control_backspace(self, event):
        return self._delete_word(event, self.config.break_chars)

    def _delete_word(self, event, stopping_chars: list[str]):
        cursor_pos = self.index(tk.INSERT)

        if not stopping_chars:
            self.delete(0, cursor_pos)
            return "break"

        pattern = f"[{''.join(map(re.escape, stopping_chars))}]"
        text_up_to_cursor = self.get()[:cursor_pos]

        last_stop_index = -1
        match = re.finditer(pattern, text_up_to_cursor)

        for m in match:
            if m.end() == cursor_pos:
                continue
            last_stop_index = m.start()

        self.delete(last_stop_index + 1, cursor_pos)
        return "break"
