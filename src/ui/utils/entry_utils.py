import tkinter as tk
from typing import Optional
from ui.custom.custom_entry import CustomEntry, CustomEntryConfig


def create_labeled_entry(
        parent: tk.Tk,
        label: Optional[str] = None,
        initial_value: Optional[str] = None,
        entry_config: Optional[CustomEntryConfig] = None,
        should_focus: bool = False,
        cursor_end: bool = False,
        on_change: Optional[callable] = None,
        **kwargs) -> tk.StringVar:
    """Creates a labeled CustomEntry widget, packs it, and returns the entry."""
    label_widget = tk.Label(parent, text=label)
    label_widget.pack(anchor='w', padx=10, pady=5)

    text_var = tk.StringVar(value=initial_value)

    custom_entry = CustomEntry(parent, textvariable=text_var,
                               config=entry_config, **kwargs)

    should_focus and custom_entry.focus_set()
    cursor_end and custom_entry.icursor(tk.END)
    on_change and text_var.trace_add('write', on_change)

    custom_entry.pack(anchor='w', padx=10, fill='x', expand=True)

    return text_var
