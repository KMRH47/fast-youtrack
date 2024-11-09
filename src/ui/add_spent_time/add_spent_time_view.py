import tkinter as tk
from typing import Optional

from ui.utils.entry_utils import create_labeled_entry
from ui.custom.custom_window import CustomWindow
from ui.custom.custom_entry import CustomEntryConfig


class AddSpentTimeView:
    def __init__(self, window: CustomWindow, issue_id: Optional[str]):
        self.__window = window

        # ID Entry
        self.__issue_id_var = create_labeled_entry(
            parent=self.__window,
            initial_value=issue_id,
            label="Issue ID:",
            entry_config=CustomEntryConfig(break_chars=['-']),
            should_focus=True,
            cursor_end=True,
            on_change=self._on_issue_id_changed
        )
        self.__issue_id_change_callback = None

        # Time Entry
        self.__time_var = create_labeled_entry(
            parent=self.__window,
            label="Enter Time (e.g., 1h30m):",
            entry_config=CustomEntryConfig(break_chars=['w', 'd', 'h', 'm'])
        )

        # Description Entry
        self.__description_var = create_labeled_entry(
            parent=self.__window,
            label="Description:")

        # Type Entry
        self.__type_var = create_labeled_entry(
            parent=self.__window,
            label="Type:"
        )

        # OK Button
        ok_button = tk.Button(
            self.__window, text="OK", command=self.__window._submit, width=10)
        ok_button.pack(pady=5)

    def _bind_issue_id_change(self, callback):
        """Bind a callback function to the issue ID change event."""
        self.__issue_id_change_callback = callback

    def _on_issue_id_changed(self, *args):
        issue_id = self.__issue_id_var.get().upper()
        self.__issue_id_var.set(issue_id)
        if self.__issue_id_change_callback:
            self.__issue_id_change_callback(issue_id)

    def _get_issue_id(self) -> str:
        return self.__issue_id_var.get()

    def _get_time(self) -> str:
        return self.__time_var.get()

    def _get_description(self) -> str:
        return self.__description_var.get()

    def _get_issue_type(self) -> str:
        return self.__type_var.get()

    def _get_window(self) -> CustomWindow:
        return self.__window

    def _show(self):
        """Displays the main window."""
        self.__window.show()
