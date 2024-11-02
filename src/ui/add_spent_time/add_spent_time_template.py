import tkinter as tk
from typing import Optional
from models.general_requests import IssueUpdateRequest
from ui.custom.custom_window import CustomWindow
from ui.custom.custom_window_config import CustomWindowConfig, KeyAction
from ui.custom.custom_entry import CustomEntry, CustomEntryConfig
from ui.timer_view import TimerView
from ui.issue_view import IssueView


class AddSpentTimeTemplate:
    def __init__(self, issue_id: str):
        self.__window = CustomWindow(
            config=CustomWindowConfig(
                width=300,
                height=325,
                title="Add Spent Time",
                topmost=True,
                destroy_action=KeyAction(key='Escape'),
                submit_action=KeyAction(key='Return')
            )
        )
        self.__timer_view = TimerView(self.__window)
        self.__issue_view = IssueView(self.__window)

        self.__window.attach_windows([
            (self.__issue_view, "right"),
            (self.__timer_view, "top"),
        ])

        # Instance variables to store the latest values
        self.__issue_id_value = issue_id
        self.__time_value = ""
        self.__description_value = ""
        self.__type_value = ""

        # Issue ID
        self.__issue_id = self.create_labeled_entry(
            value=issue_id,
            label="Issue ID:",
            entry_config=CustomEntryConfig(break_chars=['-']),
            on_change=lambda *_: self._update_issue_id()
        )
        # Time
        self.__time = self.create_labeled_entry(
            label="Enter Time (e.g., 1h30m):",
            entry_config=CustomEntryConfig(break_chars=['w', 'd', 'h', 'm']),
            on_change=lambda *_: self._update_time()
        )
        # Description
        self.__description = self.create_labeled_entry(
            label="Description:", on_change=lambda *_: self._update_description()
        )
        # Type
        self.__type = self.create_labeled_entry(
            label="Type:", on_change=lambda *_: self._update_type()
        )

        # OK Button
        ok_button = tk.Button(
            self.__window, text="OK", command=self.__window._submit_on_action, width=10)
        ok_button.pack(pady=5)

    def show(self) -> tuple[str, IssueUpdateRequest]:
        """Displays the main window and all attached windows."""
        self.__window.show()

        # Return the latest captured values
        return (self.get_issue_id(), IssueUpdateRequest(
            description=self.get_description(),
            time=self.get_time(),
            type=self.get_issue_type()
        ))

    

    # Internal methods to update instance variables
    def _update_issue_id(self):
        self.__issue_id_value = self.__issue_id.get()

    def _update_time(self):
        self.__time_value = self.__time.get()

    def _update_description(self):
        self.__description_value = self.__description.get()

    def _update_type(self):
        self.__type_value = self.__type.get()

    # Getter methods to retrieve stored values
    def get_issue_id(self) -> str:
        return self.__issue_id_value

    def get_time(self) -> str:
        return self.__time_value

    def get_description(self) -> str:
        return self.__description_value

    def get_issue_type(self) -> str:
        return self.__type_value

    def create_labeled_entry(self,
                             value: Optional[str] = None,
                             label: Optional[str] = None,
                             entry_config=None, on_change=None,
                             **kwargs) -> CustomEntry:
        """Creates a labeled CustomEntry widget and returns the entry."""
        label_widget = tk.Label(self.__window, text=label)
        label_widget.pack(anchor='w', padx=10, pady=5)

        # Initialize StringVar and set it as the textvariable for the entry
        text_var = tk.StringVar(value=value)
        custom_entry = CustomEntry(self.__window, textvariable=text_var,
                                   config=entry_config, **kwargs)
        custom_entry.pack(anchor='w', padx=10, fill='x', expand=True)

        # Attach change listener if provided
        if on_change:
            text_var.trace_add('write', on_change)

        return custom_entry
