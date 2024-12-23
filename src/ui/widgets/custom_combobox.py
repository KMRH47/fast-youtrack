import logging
from tkinter import ttk

from typing import Optional

from ui.widgets.custom_entry import CustomEntryConfig


logger = logging.getLogger(__name__)


class CustomComboboxConfig(CustomEntryConfig):
    values: list[str]

class CustomCombobox(ttk.Combobox):

    def __init__(self, master, config: Optional[CustomComboboxConfig] = None, **kwargs):
        super().__init__(master=master, **kwargs, values=config.values)


