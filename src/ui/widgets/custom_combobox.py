import logging
from typing import Optional, TypeVar, Generic

from tkinter import ttk

from ui.widgets.custom_entry import CustomEntryConfig


logger = logging.getLogger(__name__)


T = TypeVar("T")


class CustomComboboxConfig(CustomEntryConfig, Generic[T]):
    values: dict[str, T]
    initial_value: str


class CustomCombobox(ttk.Combobox, Generic[T]):

    def __init__(
        self, master, config: Optional[CustomComboboxConfig[T]] = None, **kwargs
    ):
        values = list(config.values.keys()) if config and config.values else []
        super().__init__(master=master, **kwargs, values=values)
        
        if config:
            self.set(config.initial_value or "")
        self.__values = config.values if config else {}

    def get(self) -> T | str:
        """Get the mapped value if values exist, otherwise return the display value."""
        display_value = super().get()
        if self.__values:
            return self.__values.get(display_value, display_value)
        return display_value
