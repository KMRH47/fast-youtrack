import tkinter as tk
import re

class CustomEntryConfig:
    """Configuration object for CustomEntry."""
    def __init__(self, break_chars: list[str] = None):
        self.break_chars = break_chars if break_chars is not None else []

class CustomEntry(tk.Entry):
    def __init__(self, master=None, config: CustomEntryConfig = None, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config if config is not None else CustomEntryConfig()
        self.bind('<Control-BackSpace>', self._on_control_backspace)

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
