import logging
from typing import Optional

import tkinter as tk

from ui.widgets.custom_combobox import CustomCombobox, CustomComboboxConfig
from ui.widgets.custom_entry import CustomEntry, CustomEntryConfig
from ui.widgets.custom_date_entry import CustomDateEntry, CustomDateEntryConfig

logger = logging.getLogger(__name__)


def create_labeled_entry(
    parent: tk.Tk, label: str = "", config: Optional[CustomEntryConfig] = None, **kwargs
) -> CustomEntry:
    tk.Label(parent, text=label).pack(anchor="w", padx=10, pady=5)
    entry = CustomEntry(master=parent, config=config, **kwargs)
    entry.pack(anchor="w", padx=10, fill="x", expand=True)

    if not config:
        return entry

    if config.initial_value:
        entry.delete(0, tk.END)
        entry.insert(0, config.initial_value)
    config.force_focus and parent.after(0, entry.focus_force)
    config.cursor_end and entry.icursor(tk.END)

    if not (config.validation_func or config.on_change):
        return entry

    was_invalid = False
    if config.validation_func:
        initial_border = entry["highlightbackground"]

        def validate(value):
            nonlocal was_invalid
            is_valid = config.validation_func(value)
            entry.configure(
                highlightthickness=1 if not is_valid else 0,
                highlightbackground="red" if not is_valid else initial_border,
                highlightcolor="red" if not is_valid else initial_border,
            )
            was_invalid = not is_valid
            logger.info(f"Validation result for '{value}': {is_valid}")
            return True

        def on_change(event):
            was_invalid and validate(entry.get())
            config.on_change and config.on_change(event)

        entry.configure(
            validate="focusout",
            validatecommand=(entry.register(validate), "%P"),
        )
        entry.bind("<Return>", lambda _: validate(entry.get()))
        entry.bind("<KeyRelease>", on_change)
    elif config.on_change:
        entry.bind("<KeyRelease>", config.on_change)

    return entry


def create_labeled_date_entry(
    parent: tk.Tk,
    label: Optional[str] = None,
    config: Optional[CustomDateEntryConfig] = None,
    **kwargs,
) -> CustomDateEntry:
    label_widget = tk.Label(parent, text=label)
    label_widget.pack(anchor="w", padx=10, pady=5)

    date_entry = CustomDateEntry(parent, config=config, **kwargs)
    date_entry.pack(anchor="w", padx=10, fill="x", expand=True)

    return date_entry


def create_labeled_combobox(
    parent, label: Optional[str] = None, config: Optional[CustomComboboxConfig] = None
) -> CustomCombobox:
    label_widget = tk.Label(parent, text=label)
    label_widget.pack(anchor="w", padx=10, pady=5)
    combobox = CustomCombobox(master=parent, config=config)
    combobox.pack(anchor="w", padx=10, fill="x", expand=True)
    return combobox
