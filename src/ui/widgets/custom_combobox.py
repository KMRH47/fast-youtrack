import logging
from typing import Optional, TypeVar, Generic

from tkinter import ttk

from ui.widgets.custom_entry import CustomEntryConfig


logger = logging.getLogger(__name__)


T = TypeVar("T")


class CustomComboboxConfig(CustomEntryConfig, Generic[T]):
    values: list[str]
    value_map: Optional[dict[str, T]] = None


class CustomCombobox(ttk.Combobox, Generic[T]):

    def __init__(
        self, master, config: Optional[CustomComboboxConfig[T]] = None, **kwargs
    ):
        super().__init__(
            master=master, **kwargs, values=config.values if config else []
        )
        if config:
            self.set(config.initial_value or "")
        self.__value_map = config.value_map if config else None

    def get(self) -> T | str:
        """Get the mapped value if a mapper exists, otherwise return the display value."""
        display_value = super().get()
        if self.__value_map is not None:
            return self.__value_map.get(display_value, display_value)
        return display_value
