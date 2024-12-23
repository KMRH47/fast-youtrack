import logging
import tkinter as tk
import re

from typing import Callable, Optional
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class CustomEntryConfig(BaseModel):
    initial_value: Optional[str] = None
    break_chars: Optional[list[str]] = None
    force_focus: bool = False
    cursor_end: bool = False
    validation_func: Optional[Callable[[str], bool]] = None
    on_change: Optional[Callable] = None


class CustomEntry(tk.Entry):
    __break_chars: list[str]
    text_var: tk.StringVar

    def __init__(
        self, master=None, config: Optional[CustomEntryConfig] = None, **kwargs
    ):
        super().__init__(master=master, **kwargs)
        self.text_var = tk.StringVar()
        self.config = config or CustomEntryConfig()
        self.__break_chars = self.config.break_chars or []
        self.configure(textvariable=self.text_var)

        # Event bindings (Control-BackSpace) and cursor position setup remain here
        self.bind("<Control-BackSpace>", self._on_backspace)

    def _validate(self, validation_func: Callable[[str], bool]):
        return validation_func(self.text_var.get())

    def _on_backspace(self, event):
        cursor_pos = self.index(tk.INSERT)
        text_up_to_cursor = self.text_var.get()[:cursor_pos]

        if not self.__break_chars:
            self._delete_word(cursor_pos, text_up_to_cursor)

        pattern = f"[{''.join(map(re.escape, self.__break_chars))}]"
        text_up_to_cursor = self.get()[:cursor_pos]

        last_stop_index = -1
        match = re.finditer(pattern, text_up_to_cursor)

        for m in match:
            if m.end() == cursor_pos:
                continue
            last_stop_index = m.start()

        self.delete(last_stop_index + 1, cursor_pos)
        return "break"

    def _delete_word(self, cursor_pos: int, text: str):
        reversed_text = text[::-1]

        for i, char in enumerate(reversed_text):
            last_index = len(reversed_text) - 1 == i

            if last_index:
                self.delete(0, cursor_pos)
                break

            adjacent_char = reversed_text[i + 1]

            if char != " " and adjacent_char == " ":
                self.delete(cursor_pos - i, cursor_pos)
                break
