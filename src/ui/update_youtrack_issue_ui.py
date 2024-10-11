import random
import re
import time
import logging
import tkinter as tk

from typing import List, Optional
from tkinter import ttk

from services.youtrack_service import YouTrackService
from models.issue_update_request import Author, Duration, IssueUpdateRequest
from errors.user_cancelled_error import UserCancelledError
from models.general_responses import Issue, StateBundleElement
from models.issue_states import BundleEnums
from ui.issue_view import IssueView


logger = logging.getLogger(__name__)


class IssueUpdateRequestUI:
    def __init__(self, youtrack_service: YouTrackService):
        self.root = tk.Tk()
        self.root.title("Update YouTrack Issue")
        self.root.attributes('-topmost', True)
        self.__youtrack_service = youtrack_service
        self.__issue: Issue | None = None
        self.__issue_view: IssueView | None = None
        self.__issue_update_request: IssueUpdateRequest | None = None
        self.__start_time = time.time()

        # Window size and position
        window_width = 300
        window_height = 325
        position_right = int(
            self.root.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(
            self.root.winfo_screenheight() / 2 - window_height / 2)
        self.root.geometry(
            f"{window_width}x{window_height}+{position_right}+{position_down}")
        self.root.resizable(False, False)

    def prompt(self, issue_id: str) -> Optional[IssueUpdateRequest]:
        # Bind "Escape" key to close the window
        self.root.bind("<Escape>", self._on_cancel)
        self.root.bind("<Return>", self._on_submit)

        # Issue ID
        self.debounce_id = None
        tk.Label(self.root, text="Issue ID:").pack(
            anchor='w', padx=10, pady=5)

        # Create a StringVar to monitor changes
        self.issue_id_var = tk.StringVar()

        # Bind the change of the variable with a debounced function
        self.issue_id_var.trace_add(['write'], self._on_issue_id_changed)
        self.issue_id_var.set(issue_id)

        self.issue_id_entry = tk.Entry(
            self.root, textvariable=self.issue_id_var)
        self.issue_id_entry.pack(
            anchor='w', padx=10, fill='x', expand=True)
        self.issue_id_entry.icursor(tk.END)
        self.issue_id_entry.focus_force()

        # Enter Time
        tk.Label(self.root, text="Enter Time (e.g., 1h30m):").pack(
            anchor='w', padx=10)
        self.time_entry = tk.Entry(self.root)
        self.time_entry.pack(anchor='w', padx=10, fill='x', expand=True)

        # Description
        tk.Label(self.root, text="Description:").pack(anchor='w', padx=10)
        self.description_entry = tk.Entry(self.root)
        self.description_entry.pack(
            anchor='w', padx=10, pady=5, fill='x', expand=True)

        # Type
        tk.Label(self.root, text="Type:").pack(anchor='w', padx=10)
        self.type_entry = tk.Entry(self.root)
        self.type_entry.pack(anchor='w', padx=10, pady=5,
                             fill='x', expand=True)

        # Issue State ComboBox
        tk.Label(self.root, text="Current State:").pack(
            anchor='w', padx=10)
        self.selected_issue_state_var = tk.StringVar()
        self.issue_state_combobox = ttk.Combobox(
            self.root, values=self._get_available_issue_states(), textvariable=self.selected_issue_state_var)
        self.issue_state_combobox.pack(
            anchor='w', padx=10, pady=5, fill='x', expand=True)
        self.issue_state_combobox.bind(
            '<<ComboboxSelected>>', self._on_issue_state_change)
        self.issue_state_combobox.bind(
            '<KeyRelease>', self._on_issue_state_change)

        # Elapsed Time
        self.elapsed_time_label = tk.Label(
            self.root, text="Elapsed Time: 00:00:00")
        self.elapsed_time_label.pack(padx=10, fill='x', pady=5)
        self.elapsed_time_label.config(anchor='center')

        # OK Button
        ok_button = tk.Button(self.root, text="OK",
                              command=self._on_submit, width=10)
        ok_button.pack(pady=5)

        # Bind Control-BackSpace for deleting words
        self.issue_id_entry.bind(
            '<Control-BackSpace>', lambda event: self._delete_word(event, ['-']))
        self.time_entry.bind(
            '<Control-BackSpace>', lambda event: self._delete_word(event, ['d', 'h', 'm']))
        self.description_entry.bind(
            '<Control-BackSpace>', lambda event: self._delete_word(event, []))
        self.type_entry.bind('<Control-BackSpace>',
                             lambda event: self._delete_word(event, []))

        logger.info(f"Prompting for issue update request...")

        self.__issue_view = IssueView(self.root, self.__issue)
        self._update_elapsed_time()
        self.root.mainloop()

        if self.__issue_update_request is None:
            raise UserCancelledError()

        return self.__issue_update_request

    def _on_issue_id_changed(self, *args):
        if self.debounce_id is not None:
            self.root.after_cancel(self.debounce_id)

        issue_id = self.issue_id_var.get()

        if not issue_id_valid(issue_id):
            return

        def debounce():
            self.__issue = self.__youtrack_service.get_issue(issue_id)
            _get_issue_state = self._get_issue_state()
            self.selected_issue_state_var.set(_get_issue_state)
            if self.__issue_view:
                self.__issue_view.update_issue(self.__issue)
            else:
                self.__issue_view = IssueView(self.root, self.__issue)

        self.debounce_id = self.root.after(random.randint(253, 333), debounce)

    def _on_cancel(self, event=None):
        self.root.destroy()

    def _get_issue_state(self) -> str:
        for field in self.__issue.fields:
            if field.projectCustomField and field.projectCustomField.bundle:
                if field.projectCustomField.bundle.id == BundleEnums.state:
                    return field.value.name

    def _get_available_issue_states(self):
        issue_states: list[StateBundleElement] = self.__youtrack_service.get_bundle(
            BundleEnums.state)
        return [state.name for state in issue_states if state.name]

    def _on_issue_state_change(self, event):
        if self.debounce_id:
            self.root.after_cancel(self.debounce_id)

        def debounce():
            if not self._state_valid():
                self._apply_error_style(self.issue_state_combobox)
            else:
                self._reset_style(self.issue_state_combobox)
            self.issue_state_combobox['values'] = self._get_available_issue_states(
            )

        self.debounce_id = self.root.after(random.randint(253, 333), debounce)

    def _delete_word(self, event, stopping_chars: List[str]):
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

    def _state_valid(self) -> bool:
        current_issue_state = self.selected_issue_state_var.get()
        return (
            current_issue_state is None or current_issue_state == "" or
            current_issue_state in self.issue_state_combobox['values']
        )

    def _duration_valid(self) -> bool:
        time_entry_text = self.time_entry.get()
        duration_minutes = self._convert_time_to_minutes(time_entry_text)
        return duration_minutes is not None

    def _issue_update_valid(self) -> bool:
        return (
            issue_id_valid(self.issue_id_var.get()) and
            self._duration_valid() and
            self._state_valid()
        )

    def _update_elapsed_time(self):
        elapsed = int(time.time() - self.__start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.elapsed_time_label.config(text=f"Elapsed Time: {time_string}")
        self.root.after(1000, self._update_elapsed_time)

    def _convert_time_to_minutes(self, time_str: str) -> int | None:
        def extract_time(unit: str) -> int:
            match = re.search(rf"(\d+){unit}", time_str.strip())
            return int(match.group(1)) if match else 0

        days_in_minutes = extract_time('d') * 24 * 60
        hours_in_minutes = extract_time('h') * 60

        total_minutes = days_in_minutes + hours_in_minutes + extract_time('m')

        return total_minutes if total_minutes > 0 else None

    def _on_submit(self):
        try:
            if not self._issue_update_valid():
                logger.error("Invalid issue update request.")
                return

            logger.info("Valid issue update request.")

            # Convert time entry to minutes using the function
            duration_minutes = self._convert_time_to_minutes(
                self.time_entry.get())

            # Create the IssueUpdateRequest with optional duration and other fields
            self.__issue_update_request = IssueUpdateRequest(
                author=Author(id=self.__youtrack_service.get_user_info().id),
                duration=Duration(
                    minutes=duration_minutes) if duration_minutes is not None else None,
                type=issue_type,
                text=self.description_entry.get() or None
            )

            logger.info(f"issue_update_request: {self.__issue_update_request}")
            self.root.destroy()
        except Exception as e:
            logger.error(e)
            self.root.destroy()
            raise e


def issue_id_valid(issue_id: str) -> bool:
    return re.match(r"^[A-Za-z]+-\d+$", issue_id)
