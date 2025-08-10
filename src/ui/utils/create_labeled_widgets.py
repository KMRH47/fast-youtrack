import logging
from typing import Optional, Callable, Tuple

import tkinter as tk
from tkinter import ttk

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

    config.force_focus and parent.after(0, entry.focus_force)
    config.cursor_end and entry.icursor(tk.END)

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


def create_labeled_compound_entry(
    parent: tk.Tk,
    label: str,
    left_value: str = "",
    right_value: str = "",
    separator: str = "-",
    left_width: int = 4,
    left_readonly: bool = True,
    on_change: Optional[Callable] = None,
    focus_right: bool = True,
) -> Tuple[tk.StringVar, tk.StringVar, ttk.Entry, ttk.Entry]:
    """Create a compound entry with left (readonly) and right (editable) parts separated by a dash."""
    issue_row = tk.Frame(parent)
    issue_row.pack(fill="x", expand=True, padx=10, pady=(10, 5))

    tk.Label(issue_row, text=label).grid(row=0, column=0, sticky="w", padx=(0, 6))

    left_var = tk.StringVar(value=left_value)
    left_entry = ttk.Entry(
        issue_row,
        textvariable=left_var,
        state="readonly" if left_readonly else "normal",
        width=left_width,
        takefocus=not left_readonly,
    )
    left_entry.grid(row=0, column=1, sticky="w")

    tk.Label(issue_row, text=separator).grid(row=0, column=2, padx=6)

    right_var = tk.StringVar(value=right_value)
    right_entry = ttk.Entry(issue_row, textvariable=right_var)
    right_entry.grid(row=0, column=3, sticky="ew")

    issue_row.grid_columnconfigure(1, weight=0, minsize=48)
    issue_row.grid_columnconfigure(3, weight=1)

    if on_change:
        right_entry.bind("<KeyRelease>", on_change)

    if focus_right:
        parent.after_idle(right_entry.focus_set)

    return left_var, right_var, left_entry, right_entry
