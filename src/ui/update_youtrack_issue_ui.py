import re
import time
import logging
import tkinter as tk

from typing import List, Optional
from tkinter import ttk

from models.issue_update import IssueUpdate
from services.youtrack_service import YouTrackService


logger = logging.getLogger(__name__)


class IssueUpdateRequestUI:
    def __init__(self, youtrack_service: YouTrackService):
        self.__youtrack_service = youtrack_service
        self.__issue_update_request = None

    def prompt(self, initial_request: IssueUpdate) -> Optional[IssueUpdate]:
        try:
            self.root = tk.Tk()
            self.root.title("Update YouTrack Issue")
            self.root.attributes('-topmost', True)

            window_width = 300
            window_height = 325
            position_right = int(
                self.root.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(
                self.root.winfo_screenheight() / 2 - window_height / 2)
            self.root.geometry(
                f"{window_width}x{window_height}+{position_right}+{position_down}")
            self.root.resizable(False, False)

            self.__start_time = time.time()

            # Bind "Escape" key to close the window
            self.root.bind("<Escape>", self.__on_escape)
            self.root.bind("<Return>", self.__on_return)

            # Issue ID
            tk.Label(self.root, text="Issue ID:").pack(anchor='w', padx=10, pady=5)
            self.issue_id_entry = tk.Entry(self.root)
            self.issue_id_entry.insert(0, initial_request.id)
            self.issue_id_entry.pack(anchor='w', padx=10, fill='x', expand=True)
            self.issue_id_entry.focus_force()

            # Enter Time
            tk.Label(self.root, text="Enter Time (e.g., 1h30m):").pack(
                anchor='w', padx=10)
            self.time_entry = tk.Entry(self.root)
            self.time_entry.insert(0, initial_request.time)
            self.time_entry.pack(anchor='w', padx=10, fill='x', expand=True)

            # Description
            tk.Label(self.root, text="Description:").pack(anchor='w', padx=10)
            self.description_entry = tk.Entry(self.root)
            self.description_entry.insert(0, initial_request.description)
            self.description_entry.pack(
                anchor='w', padx=10, pady=5, fill='x', expand=True)

            # Type
            tk.Label(self.root, text="Type:").pack(anchor='w', padx=10)
            self.type_entry = tk.Entry(self.root)
            self.type_entry.insert(0, initial_request.type)
            self.type_entry.pack(anchor='w', padx=10, pady=5,
                                 fill='x', expand=True)

            # Issue State ComboBox
            tk.Label(self.root, text="Current State:").pack(anchor='w', padx=10)
            current_issue_state = initial_request.state or ""
            self.selected_issue_state_var = tk.StringVar(value=current_issue_state)
            self.issue_state_combobox = ttk.Combobox(
                self.root, values=self.__get_available_issue_states(), textvariable=self.selected_issue_state_var)
            self.issue_state_combobox.pack(
                anchor='w', padx=10, pady=5, fill='x', expand=True)
            self.issue_state_combobox.bind(
                '<<ComboboxSelected>>', self.__on_issue_state_change)
            self.issue_state_combobox.bind(
                '<KeyRelease>', self.__on_issue_state_change)

            # Elapsed Time
            self.elapsed_time_label = tk.Label(
                self.root, text="Elapsed Time: 00:00:00")
            self.elapsed_time_label.pack(padx=10, fill='x', pady=5)
            self.elapsed_time_label.config(anchor='center')

            # OK Button
            ok_button = tk.Button(self.root, text="OK",
                                  command=self.__on_ok_click, width=10)
            ok_button.pack(pady=5)

            # Bind Control-BackSpace for deleting words
            self.issue_id_entry.bind(
                '<Control-BackSpace>', lambda event: self.__delete_word(event, ['-']))
            self.time_entry.bind(
                '<Control-BackSpace>', lambda event: self.__delete_word(event, ['d', 'h', 'm', 's']))
            self.description_entry.bind(
                '<Control-BackSpace>', lambda event: self.__delete_word(event, []))
            self.type_entry.bind('<Control-BackSpace>',
                                 lambda event: self.__delete_word(event, []))

            # Start updating elapsed time
            self.__update_elapsed_time()

            self.root.mainloop()
            return self.__issue_update_request
        except Exception as e:
            self.root.destroy()
            raise e

    def __on_escape(self, event=None):
        self.root.destroy()

    def __on_return(self, event=None):
        self.__on_ok_click()

    def __get_available_issue_states(self):
        available_issue_states = self.__youtrack_service.get_work_item_types()
        active_issue_state = self.selected_issue_state_var.get()
        return [issue_state.name for issue_state in available_issue_states if issue_state != active_issue_state]

    def __on_issue_state_change(self, event):
        if not self.__is_issue_state_valid():
            self._apply_error_style(self.issue_state_combobox)
        else:
            self._reset_style(self.issue_state_combobox)
        self.issue_state_combobox['values'] = self.__get_available_issue_states(
        )

    def __delete_word(self, event, stopping_chars: List[str]):
        entry: tk.Entry = event.widget
        cursor_pos = entry.index(tk.INSERT)

        if not stopping_chars:
            entry.delete(0, cursor_pos)
            return "break"

        pattern = f"[{''.join(map(re.escape, stopping_chars))}]"
        text_up_to_cursor = entry.get()[:cursor_pos]

        last_stop_index = -1
        match = re.finditer(pattern, text_up_to_cursor)

        for m in match:
            if m.end() == cursor_pos:
                continue
            last_stop_index = m.start()

        entry.delete(last_stop_index + 1, cursor_pos)
        return "break"

    def _apply_error_style(self, widget):
        """Apply error styling to a widget."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Error.TCombobox', fieldbackground='white',
                        bordercolor='red', borderwidth=2)
        widget.config(style='Error.TCombobox')

    def _reset_style(self, widget):
        """Reset the style of a widget to default."""
        widget.config(style='TCombobox')

    def __is_issue_state_valid(self):
        current_issue_state = self.selected_issue_state_var.get()
        return current_issue_state in self.__get_available_issue_states()

    def __update_elapsed_time(self):
        elapsed = int(time.time() - self.__start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.elapsed_time_label.config(text=f"Elapsed Time: {time_string}")
        self.root.after(1000, self.__update_elapsed_time)

    def __on_ok_click(self):
        if not self.__is_issue_state_valid():
            return

        self.__issue_update_request = IssueUpdate(
            id=self.issue_id_entry.get(),
            time=self.time_entry.get(),
            description=self.description_entry.get(),
            type=self.type_entry.get(),
            state=self.selected_issue_state_var.get()
        )
        self.root.destroy()
