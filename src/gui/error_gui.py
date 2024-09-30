import tkinter as tk


def display_error_dialog(message: str) -> None:
    root = tk.Tk()
    root.withdraw()

    error_window = tk.Toplevel(root)
    error_window.title("Error")

    label = tk.Label(error_window, text=message, font=("Arial", 16))
    label.pack(padx=20, pady=20)

    close_button = tk.Button(error_window, text="OK",
                             command=error_window.destroy)
    close_button.pack(pady=10)

    error_window.update_idletasks()
    window_width = error_window.winfo_width()
    window_height = error_window.winfo_height()
    position_right = int(
        error_window.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(
        error_window.winfo_screenheight() / 2 - window_height / 2)
    error_window.geometry(f"+{position_right}+{position_down}")

    def ensure_focus():
        if not close_button.focus_get():
            close_button.focus_set()
            error_window.after(100, ensure_focus)

    error_window.after(1, ensure_focus)
    error_window.bind('<Return>', lambda event: error_window.destroy())

    root.mainloop()
