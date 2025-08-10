import tkinter as tk


def display_error_dialog(message: str) -> None:
    root = tk.Tk()
    root.withdraw()

    error_window = tk.Toplevel(root)
    error_window.title("Error")
    error_window.attributes("-topmost", True)

    frame = tk.Frame(error_window)
    frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    text = tk.Text(frame, wrap=tk.WORD, width=50, height=10, font=("Arial", 12))
    text.insert("1.0", message)
    text.configure(state="disabled")
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=text.yview)

    text.see("end")  # Scroll to bottom

    def _close_all():
        try:
            error_window.destroy()
        finally:
            try:
                root.destroy()
            except Exception:
                pass

    close_button = tk.Button(error_window, text="OK", command=_close_all)
    close_button.pack(pady=10)

    error_window.update_idletasks()
    window_width = error_window.winfo_width()
    window_height = error_window.winfo_height()
    position_right = int(error_window.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(error_window.winfo_screenheight() / 2 - window_height / 2)
    error_window.geometry(f"+{position_right}+{position_down}")

    error_window.focus_set()
    close_button.focus_force()
    error_window.bind("<Return>", lambda event: _close_all())
    error_window.bind("<Escape>", lambda event: _close_all())

    try:
        root.mainloop()
    finally:
        try:
            root.destroy()
        except Exception:
            pass
