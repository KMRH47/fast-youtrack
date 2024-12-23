import logging
import tkinter as tk
from tkcalendar import DateEntry
from typing import Optional

from ui.custom.custom_combobox import CustomCombobox, CustomComboboxConfig
from ui.custom.custom_entry import CustomEntry, CustomEntryConfig

logger = logging.getLogger(__name__)


class CustomDateEntryConfig(CustomEntryConfig):
    date_format: Optional[str] = "yyyy-mm-dd"


def create_labeled_entry(
    parent: tk.Tk, label: str = "", config: Optional[CustomEntryConfig] = None, **kwargs
) -> tk.StringVar:
    """Creates a labeled CustomEntry widget, packs it, and returns the entry."""
    label_widget = tk.Label(parent, text=label)
    label_widget.pack(anchor="w", padx=10, pady=5)

    custom_entry = CustomEntry(master=parent, config=config, **kwargs)
    custom_entry.pack(anchor="w", padx=10, fill="x", expand=True)

    if config:
        custom_entry.text_var.set(config.initial_value or "")
        config.on_change and custom_entry.text_var.trace_add("write", config.on_change)
        config.force_focus and parent.after(0, lambda: parent.after(0, custom_entry.focus_force))
        config.cursor_end and custom_entry.icursor(tk.END)

        if config.validation_func:
            validate_command = (
                custom_entry.register(lambda v: config.validation_func(v)),
                "%P",
            )
            custom_entry.configure(
                validate="focusout", validatecommand=validate_command
            )

    return custom_entry.text_var


def create_labeled_date_entry(
    parent: tk.Tk,
    label: Optional[str] = None,
    config: Optional[CustomDateEntryConfig] = None,
    **kwargs
) -> tk.StringVar:
    label_widget = tk.Label(parent, text=label)
    label_widget.pack(anchor="w", padx=10, pady=5)

    text_var = tk.StringVar(value=config.initial_value)
    date_entry = DateEntry(
        parent, textvariable=text_var, date_pattern=config.date_format, **kwargs
    )
    date_entry.pack(anchor="w", padx=10, fill="x", expand=True)

    if config.on_change:
        text_var.trace_add("write", config.on_change)

    return text_var


def create_labeled_combobox(
    parent, label: Optional[str] = None, config: Optional[CustomComboboxConfig] = None
) -> tk.StringVar:
    logger.info("Creating labeled combobox, config: %s", config)
    label_widget = tk.Label(parent, text=label)
    label_widget.pack(anchor="w", padx=10, pady=5)

    text_var = tk.StringVar(value=config.initial_value)
    combobox = CustomCombobox(master=parent, config=config, textvariable=text_var)

    combobox.pack(anchor="w", padx=10, fill="x", expand=True)

    return text_var
