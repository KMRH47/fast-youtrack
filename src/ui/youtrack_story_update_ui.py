import logging
import tkinter as tk
from tkinter import ttk
from typing import List
import time

logger = logging.getLogger(__name__)


def display_youtrack_story_update(available_states: List[str]) -> None:
    root = tk.Tk()
    root.title("Update YouTrack Story")

    window_width = 300
    window_height = 325
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry(
        f"{window_width}x{window_height}+{position_right}+{position_down}")
    root.resizable(False, False)

    start_time = time.time()

    # Function to close the window on "Escape" key press
    def on_escape(event=None):
        root.destroy()

    def on_return(event=None):
        on_ok_click()

    # Bind "Escape" key to close the window
    root.bind("<Escape>", on_escape)
    root.bind("<Return>", on_return)

    # Issue ID
    tk.Label(root, text="Issue ID:").pack(anchor='w', padx=10, pady=(10, 0))
    issue_id_entry = tk.Entry(root)
    issue_id_entry.insert(0, "AGI-")  # Pre-fill with a default value if needed
    issue_id_entry.pack(anchor='w', padx=10, pady=(0, 5),
                        fill='x', expand=True)
    issue_id_entry.focus_force()

    # Enter Time
    tk.Label(root, text="Enter Time (e.g., 1h30m):").pack(anchor='w', padx=10)
    time_entry = tk.Entry(root)
    time_entry.pack(anchor='w', padx=10, fill='x', expand=True)

    # Description
    tk.Label(root, text="Description:").pack(anchor='w', padx=10)
    description_text = tk.Entry(root)
    description_text.pack(anchor='w', padx=10,
                          pady=(0, 5), fill='x', expand=True)

    # Type
    tk.Label(root, text="Type:").pack(anchor='w', padx=10)
    type_entry = tk.Entry(root)
    type_entry.pack(anchor='w', padx=10, pady=(0, 5), fill='x', expand=True)

    # State ComboBox
    tk.Label(root, text="Current State:").pack(
        anchor='w', padx=10, pady=(10, 0))
    state_combobox = ttk.Combobox(root, values=available_states)
    state_combobox.set(available_states[0])
    state_combobox.pack(anchor='w', padx=10, pady=(0, 5),
                        fill='x', expand=True)

    # Elapsed Time
    elapsed_time_label = tk.Label(root, text="Elapsed Time: 00:00:00")
    elapsed_time_label.pack(padx=10, pady=(10, 0), fill='x')
    elapsed_time_label.config(anchor='center')

    def update_elapsed_time():
        elapsed = int(time.time() - start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elapsed_time_label.config(text=f"Elapsed Time: {time_string}")
        root.after(1000, update_elapsed_time)

    def on_ok_click():
        log_message = (
            f"YouTrack Story Update\n"
            f"Issue ID: {issue_id_entry.get()}\n"
            f"Time: {time_entry.get()}\n"
            f"Description: {description_text.get()}\n"
            f"Type: {type_entry.get()}\n"
            f"State: {state_combobox.get()}"
        )
        logger.info(log_message)
        root.destroy()

    ok_button = tk.Button(root, text="OK", command=on_ok_click, width=10)
    ok_button.pack(pady=(10, 10))

    update_elapsed_time()
    root.mainloop()
