import tkinter as tk
from ui.utils.entry_utils import create_labeled_entry
from ui.custom.custom_window import CustomWindow
from ui.custom.custom_window_config import CustomWindowConfig
from ui.custom.custom_entry import CustomEntryConfig


class AddSpentTimeTemplate:
    def __init__(self, issue_id: str):
        self.__window = CustomWindow(
            config=CustomWindowConfig(
                width=300,
                height=325,
                title="Add Spent Time",
                topmost=True,
                cancel_key='Escape',
                submit_key='Return'
            )
        )

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

    def bind_issue_id_change(self, callback):
        """Bind a callback function to the issue ID change event."""
        self.__issue_id_change_callback = callback

    def _on_issue_id_changed(self, *args):
        if self.__issue_id_change_callback:
            self.__issue_id_change_callback(self.__issue_id_var.get())

    def get_issue_id(self) -> str:
        return self.__issue_id_var.get()

    def get_time(self) -> str:
        return self.__time_var.get()

    def get_description(self) -> str:
        return self.__description_var.get()

    def get_issue_type(self) -> str:
        return self.__type_var.get()

    def get_window(self) -> CustomWindow:
        return self.__window

    def show(self):
        """Displays the main window."""
        self.__window.show()
