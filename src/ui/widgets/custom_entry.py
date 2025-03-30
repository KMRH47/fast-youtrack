import logging
import re
from typing import Callable, Optional

import tkinter as tk

from ui.widgets.base_widget_config import BaseWidgetConfig


logger = logging.getLogger(__name__)


class CustomEntryConfig(BaseWidgetConfig):
    break_chars: Optional[list[str]] = None
    force_focus: bool = False
    cursor_end: bool = False
    validation_func: Optional[Callable[[str], bool]] = None


class CustomEntry(tk.Entry):
    __break_chars: list[str]
    __initial_border: str
    __is_pristine: bool

    def __init__(
        self, master=None, config: Optional[CustomEntryConfig] = None, **kwargs
    ):
        super().__init__(master=master, **kwargs)
        self.config = config or CustomEntryConfig()
        self.__break_chars = self.config.break_chars or []
        self.__initial_border = self["highlightbackground"]
        self.__is_pristine = True

        if config:
            if config.initial_value:
                self.insert(0, config.initial_value)
            if config.validation_func:
                self.config.validation_func = config.validation_func
                self.bind("<FocusOut>", lambda e: self.validate())
                self.bind("<Return>", lambda e: self.validate())

        self.bind("<KeyRelease>", self._on_change)
        self.bind("<Control-BackSpace>", self._on_backspace)

    def reset(self):
        self.delete(0, tk.END)
        self.__is_pristine = True
        self.validate()

    def validate(self) -> None:
        self.config.validation_func and self._set_validation_state(self.get())

    def _on_backspace(self, _):
        cursor_pos = self.index(tk.INSERT)
        text_up_to_cursor = self.get()[:cursor_pos]

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

    def _on_change(self, event):
        self.__is_pristine = False
        self.config.on_change and self.config.on_change(event)

    def _set_validation_state(self, value: str) -> None:
        is_valid = self.__is_pristine or self.config.validation_func(value)
        self.configure(
            highlightthickness=1 if not is_valid else 0,
            highlightbackground="red" if not is_valid else self.__initial_border,
            highlightcolor="red" if not is_valid else self.__initial_border,
        )
