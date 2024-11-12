import logging
from tkinter import ttk

from typing import Optional

from ui.custom.custom_entry import CustomEntry, CustomEntryConfig


logger = logging.getLogger(__name__)


class CustomComboboxConfig(CustomEntryConfig):
    values: list[str]


class CustomCombobox(ttk.Combobox):

    def __init__(
        self, master=None, config: Optional[CustomComboboxConfig] = None, **kwargs
    ):
        super().__init__(master, **kwargs, values=config.values)
