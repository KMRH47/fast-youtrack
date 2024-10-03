from typing import Optional
from models.issue_update_request import IssueState, IssueUpdateRequest
from tkinter import ttk
import re
import time
import logging
import tkinter as tk


logger = logging.getLogger(__name__)


def prompt_for_issue_update_request_ui(initial_update_request: IssueUpdateRequest) -> Optional[IssueUpdateRequest]:

    issue_update_request: Optional[IssueUpdateRequest] = None

    def on_escape(event=None):
        root.destroy()

    def on_return(event=None):
        on_ok_click()

    def get_available_states():
        active_state = selected_state_var.get()
        return [state for state in initial_update_request.state.available_states if state != active_state]

    def on_state_change(event):
        state_combobox['values'] = get_available_states()

    def delete_word(event, stopping_chars):
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

    root = tk.Tk()
    root.title("Update YouTrack Issue")

    window_width = 300
    window_height = 325
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry(
        f"{window_width}x{window_height}+{position_right}+{position_down}")
    root.resizable(False, False)

    start_time = time.time()

    # Bind "Escape" key to close the window
    root.bind("<Escape>", on_escape)
    root.bind("<Return>", on_return)

    # Issue ID
    tk.Label(root, text="Issue ID:").pack(anchor='w', padx=10, pady=5)
    issue_id_entry = tk.Entry(root)
    issue_id_entry.insert(0, initial_update_request.id)
    issue_id_entry.pack(anchor='w', padx=10, fill='x', expand=True)
    issue_id_entry.focus_force()

    # Enter Time
    tk.Label(root, text="Enter Time (e.g., 1h30m):").pack(anchor='w', padx=10)
    time_entry = tk.Entry(root)
    time_entry.insert(0, initial_update_request.time)
    time_entry.pack(anchor='w', padx=10, fill='x', expand=True)

    # Description
    tk.Label(root, text="Description:").pack(anchor='w', padx=10)
    description_entry = tk.Entry(root)
    description_entry.insert(0, initial_update_request.description)
    description_entry.pack(anchor='w', padx=10, pady=5, fill='x', expand=True)

    # Type
    tk.Label(root, text="Type:").pack(anchor='w', padx=10)
    type_entry = tk.Entry(root)
    type_entry.insert(0, initial_update_request.type)
    type_entry.pack(anchor='w', padx=10, pady=5, fill='x', expand=True)

    # State ComboBox
    tk.Label(root, text="Current State:").pack(anchor='w', padx=10)
    current_state = initial_update_request.state.current or ""
    selected_state_var = tk.StringVar(value=current_state)
    state_combobox = ttk.Combobox(
        root, values=get_available_states(), textvariable=selected_state_var)
    state_combobox.pack(anchor='w', padx=10, pady=5, fill='x', expand=True)
    state_combobox.bind('<<ComboboxSelected>>', on_state_change)

    # Elapsed Time
    elapsed_time_label = tk.Label(root, text="Elapsed Time: 00:00:00")
    elapsed_time_label.pack(padx=10, fill='x', pady=5)
    elapsed_time_label.config(anchor='center')

    def update_elapsed_time():
        elapsed = int(time.time() - start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elapsed_time_label.config(text=f"Elapsed Time: {time_string}")
        root.after(1000, update_elapsed_time)

    def on_ok_click():
        nonlocal issue_update_request
        issue_update_request = IssueUpdateRequest(
            id="asdasdasdasad",
            time=time_entry.get(),
            description=description_entry.get(),
            type=type_entry.get(),
            state=IssueState(
                current=selected_state_var.get(),
                available_states=get_available_states()
            )
        )
        root.destroy()

    ok_button = tk.Button(root, text="OK", command=on_ok_click, width=10)
    ok_button.pack(pady=5)

    issue_id_entry.bind('<Control-BackSpace>',
                        lambda event: delete_word(event, ['-']))
    time_entry.bind('<Control-BackSpace>',
                    lambda event: delete_word(event, ['d', 'h', 'm', 's']))
    description_entry.bind('<Control-BackSpace>',
                           lambda event: delete_word(event, []))
    type_entry.bind('<Control-BackSpace>',
                    lambda event: delete_word(event, []))

    update_elapsed_time()
    root.mainloop()
    return issue_update_request
