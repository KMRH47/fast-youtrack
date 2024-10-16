import logging
import tkinter as tk

from models.general_responses import EnumBundleElement, Issue

logger = logging.getLogger(__name__)


class IssueViewer:
    def __init__(self, parent_ui: tk.Tk, issue: Issue | None = None):
        self.parent_ui = parent_ui
        self.issue = issue
        self.window = tk.Toplevel(self.parent_ui)
        self.window.title("Issue Viewer")
        self.window.wm_attributes('-topmost', True)
        self.window.wm_attributes('-disabled', True)
        self.window.bind("<FocusIn>", self._on_focus_in)
        self._update_window_position()
        self.window.transient(self.parent_ui)
        self.window.deiconify()
        self.window.update_idletasks()
        self._bind_window_movement()

    def _initialize_window(self):
        """Initialize the Toplevel window for
        displaying issue details."""

    def _on_focus_in(self, event):
        """Redirect focus back to the main application
        window when IssueView gains focus."""
        self.parent_ui.focus_force()

    def _bind_window_movement(self):
        """Bind the Update UI window's movement to follow the IssueView."""
        self.parent_ui.bind("<Configure>", self._on_update_ui_moved)

    def _on_update_ui_moved(self, event):
        """Move the IssueView window when the Update UI window is moved."""
        self._update_window_position()

    def _update_window_position(self):
        """Position the IssueView next to the Update UI window."""
        x = self.parent_ui.winfo_x() + self.parent_ui.winfo_width() + 10
        y = self.parent_ui.winfo_y()
        self.window.geometry(f"+{x}+{y}")

    def update_issue(self, issue: Issue):
        """Update the window with new issue details."""
        self.issue = issue
        logger.info(f"Updating IssueView with issue: {issue}")
        self._build_ui()

    def _build_ui(self):
        """Draw the UI for displaying the issue details."""
        # Clear the window before redrawing
        for widget in self.window.winfo_children():
            widget.destroy()

        # Create a container frame for better layout management
        container_frame = tk.Frame(self.window, padx=10, pady=10)
        container_frame.pack(fill='both', expand=True)

        row_counter = 0

        # Created by (reporter)
        created_by_text = f"Created by: {self.issue.reporter.name}"
        tk.Label(
            container_frame,
            text=created_by_text,
            font=("Arial", 10, "bold")) \
            .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
        row_counter += 1

        # Updated by (updater), only if there is an updater
        if self.issue.updater and self.issue.updater.name:
            updated_by_text = f"Updated by: {self.issue.updater.name}"
            tk.Label(
                container_frame,
                text=updated_by_text,
                font=("Arial", 10, "bold")) \
                .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
            row_counter += 1

        summary_text = self.issue.summary if self.issue \
            and self.issue.summary else "No summary available"
        summary_text = summary_text[:100] + \
            "..." if len(summary_text) > 100 else summary_text
        tk.Label(
            container_frame,
            text="Summary:",
            font=("Arial", 10, "bold")) \
            .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
        self.summary_label = tk.Label(
            container_frame,
            text=f"{summary_text}",
            font=("Arial", 10),
            wraplength=250,
            justify="left")
        self.summary_label.grid(row=row_counter, column=1, sticky='nw')
        row_counter += 1

        description_text = self.issue.description if self.issue and \
            self.issue.description else "No description available"
        description_text = description_text[:100] + "..." if len(
            description_text) > 100 else description_text
        tk.Label(
            container_frame,
            text="Description:",
            font=("Arial", 10, "bold")) \
            .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
        self.description_label = tk.Label(
            container_frame,
            text=f"{description_text}",
            font=("Arial", 10), wraplength=250, justify="left")
        self.description_label.grid(row=row_counter, column=1, sticky='nw')
        row_counter += 1

        for field in self.issue.fields:
            if field.projectCustomField:
                field_name = field.projectCustomField.field.name \
                    if field.projectCustomField.field else "Unknown Field"
            else:
                field_name = "Unknown Field"

            if isinstance(field.value, EnumBundleElement):
                field_value = field.value.name if field.value else "No value"
            elif isinstance(field.value, list):
                field_value = ", ".join(
                    [element.name for element in field.value if element.name])\
                    if field.value else "No value"
            else:
                field_value = "No value"

            tk.Label(
                container_frame,
                text=f"{field_name}:",
                font=("Arial", 10, "bold")) \
                .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
            self.field_value_label = tk.Label(
                container_frame,
                text=f"{field_value}",
                font=("Arial", 10), wraplength=250, justify="left")
            self.field_value_label.grid(row=row_counter, column=1, sticky='nw')
            row_counter += 1
