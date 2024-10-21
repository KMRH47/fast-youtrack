import logging
import time
import tkinter as tk

logger = logging.getLogger(__name__)


class TimerView:
    def __init__(self, parent_window: tk.Tk):
        self.__parent_window = parent_window
        self.__window = None
        self.__start_time = None
        self.__timer_label = None

    def show(self):
        """Initialize and display the Timer window when called."""
        if self.__window is None:
            self.__window = tk.Toplevel(self.__parent_window)
            self.__window.title("Elapsed Time")
            self.__window.wm_attributes('-topmost', True)
            self.__window.wm_attributes('-disabled', True)
            self.__window.bind("<FocusIn>", self._on_focus_in)
            self._bind_window_movement()

            self._initialize_timer_ui()

        # Show the window and update its position
        self.__window.transient(self.__parent_window)
        self.__window.deiconify()
        self.__window.update_idletasks()
        self._update_window_position()

        # Start the timer when the window is displayed
        self.__start_time = int(time.time())
        self._update_elapsed_time()

    def _initialize_timer_ui(self):
        """Initialize the Toplevel window for displaying the timer."""
        container_frame = tk.Frame(self.__window, padx=10, pady=10)
        container_frame.pack(fill='both', expand=True)

        self.__timer_label = tk.Label(container_frame, text="Elapsed Time: 00:00:00", font=("Arial", 14, "bold"))
        self.__timer_label.pack()

    def _on_focus_in(self, event):
        """Redirect focus back to the main application window when TimerViewer gains focus."""
        self.__parent_window.focus_force()

    def _bind_window_movement(self):
        """Bind the parent window's movement to follow the TimerViewer."""
        self.__parent_window.bind("<Configure>", self._on_update_ui_moved)

    def _on_update_ui_moved(self, event):
        """Move the TimerViewer window when the parent UI window is moved."""
        self._update_window_position()

    def _update_window_position(self):
        """Position the TimerViewer next to the parent UI window."""
        x = self.__parent_window.winfo_x() + self.__parent_window.winfo_width() + 10
        y = self.__parent_window.winfo_y()
        self.__window.geometry(f"+{x}+{y}")

    def _update_elapsed_time(self):
        """Update the elapsed time label every second."""
        elapsed = int(time.time()) - self.__start_time
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.__timer_label.config(text=f"Elapsed Time: {time_string}")
        self.__window.after(1000, self._update_elapsed_time)
