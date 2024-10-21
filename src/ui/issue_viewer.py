import logging
import tkinter as tk
from models.general_responses import EnumBundleElement, Issue

logger = logging.getLogger(__name__)


class IssueView:
    def __init__(self, parent_window: tk.Tk, issue: Issue | None = None):
        self.__parent_window = parent_window
        self.__issue = issue
        self.__window = None
        self.__summary_label = None
        self.__description_label = None
        self.__field_value_label = None

    def show(self):
        """Lazy initialization and display of the IssueView window."""
        if self.__window is None:
            self.__window = tk.Toplevel(self.__parent_window)
            self.__window.title("Issue Viewer")
            self.__window.wm_attributes('-topmost', True)
            self.__window.wm_attributes('-disabled', True)
            self.__window.bind("<FocusIn>", self._on_focus_in)
            self._bind_window_movement()
            self._initialize_window()

        self.__window.transient(self.__parent_window)
        self.__window.deiconify()
        self.__window.update_idletasks()
        self._update_window_position()

    def _initialize_window(self):
        """Initialize the Toplevel window for displaying issue details."""
        self._build_ui()

    def _on_focus_in(self, event):
        """Redirect focus back to the main application window when IssueView gains focus."""
        self.__parent_window.focus_force()

    def _bind_window_movement(self):
        """Bind the parent window's movement to follow the IssueView."""
        self.__parent_window.bind("<Configure>", self._on_update_ui_moved)

    def _on_update_ui_moved(self, event):
        """Move the IssueView window when the parent UI window is moved."""
        self._update_window_position()

    def _update_window_position(self):
        """Position the IssueView next to the parent UI window."""
        if self.__window:
            x = self.__parent_window.winfo_x() + self.__parent_window.winfo_width() + 10
            y = self.__parent_window.winfo_y()
            self.__window.geometry(f"+{x}+{y}")

    def update_issue(self, issue: Issue):
        """Update the window with new issue details."""
        self.__issue = issue
        logger.info(f"Updating IssueView with issue: {issue}")
        if self.__window:  # Only update UI if window is already created
            self._build_ui()

    def _build_ui(self):
        """Draw the UI for displaying the issue details."""
        # Clear the window before redrawing
        for widget in self.__window.winfo_children():
            widget.destroy()

        # Create a container frame for better layout management
        container_frame = tk.Frame(self.__window, padx=10, pady=10)
        container_frame.pack(fill='both', expand=True)

        # If no issue, render a placeholder or blank view
        if self.__issue is None:
            tk.Label(container_frame, text="No issue to display",
                     font=("Arial", 12, "bold")).pack(pady=20)
            return  # Exit as there's no issue to display

        row_counter = 0

        # Created by (reporter)
        created_by_text = f"Created by: {self.__issue.reporter.name}"
        tk.Label(container_frame, text=created_by_text, font=("Arial", 10, "bold")) \
            .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
        row_counter += 1

        # Updated by (updater), only if there is an updater
        if self.__issue.updater and self.__issue.updater.name:
            updated_by_text = f"Updated by: {self.__issue.updater.name}"
            tk.Label(container_frame, text=updated_by_text, font=("Arial", 10, "bold")) \
                .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
            row_counter += 1

        # Summary
        summary_text = self.__issue.summary if self.__issue and self.__issue.summary else "No summary available"
        summary_text = summary_text[:100] + \
            "..." if len(summary_text) > 100 else summary_text
        tk.Label(container_frame, text="Summary:", font=("Arial", 10, "bold")) \
            .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
        self.__summary_label = tk.Label(container_frame, text=f"{summary_text}", font=("Arial", 10), wraplength=250,
                                        justify="left")
        self.__summary_label.grid(row=row_counter, column=1, sticky='nw')
        row_counter += 1

        # Description
        description_text = self.__issue.description if self.__issue and self.__issue.description else "No description available"
        description_text = description_text[:100] + "..." if len(
            description_text) > 100 else description_text
        tk.Label(container_frame, text="Description:", font=("Arial", 10, "bold")) \
            .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
        self.__description_label = tk.Label(container_frame, text=f"{description_text}", font=("Arial", 10), wraplength=250,
                                            justify="left")
        self.__description_label.grid(row=row_counter, column=1, sticky='nw')
        row_counter += 1

        # Display other fields
        for field in self.__issue.fields:
            if field.projectCustomField:
                field_name = field.projectCustomField.field.name if field.projectCustomField.field else "Unknown Field"
            else:
                field_name = "Unknown Field"

            if isinstance(field.value, EnumBundleElement):
                field_value = field.value.name if field.value else "No value"
            elif isinstance(field.value, list):
                field_value = ", ".join(
                    [element.name for element in field.value if element.name]) if field.value else "No value"
            else:
                field_value = "No value"

            tk.Label(container_frame, text=f"{field_name}:", font=("Arial", 10, "bold")) \
                .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
            self.__field_value_label = tk.Label(container_frame, text=f"{field_value}", font=("Arial", 10), wraplength=250,
                                                justify="left")
            self.__field_value_label.grid(
                row=row_counter, column=1, sticky='nw')
            row_counter += 1
