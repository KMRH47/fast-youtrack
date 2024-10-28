from models.general_responses import EnumBundleElement, Issue
import tkinter as tk
from typing import Optional
import logging

from ui.custom.custom_toplevel import CustomTopLevel

logger = logging.getLogger(__name__)


class IssueView(CustomTopLevel):
    def __init__(self, parent_window: tk.Tk, issue: Optional[Issue] = None):
        super().__init__(parent_window, title="Issue Viewer", topmost=True)
        self.__issue = issue
        self.__summary_label: Optional[tk.Label] = None
        self.__description_label: Optional[tk.Label] = None
        self.__field_value_label: Optional[tk.Label] = None

    def update_issue(self, issue: Issue) -> None:
        """Update the window with new issue details."""
        self.__issue = issue
        logger.info(f"Updating IssueView with issue: {issue}")
        if self.get_window():  # Only update UI if window is already created
            self._build_ui()

    def _build_ui(self) -> None:
        """Build the UI for displaying issue details."""
        window = self.get_window()
        if not window:
            return

        # Clear existing widgets
        for widget in window.winfo_children():
            widget.destroy()

        # Create container frame
        container_frame = tk.Frame(window, padx=10, pady=10)
        container_frame.pack(fill='both', expand=True)

        # Handle no issue case
        if self.__issue is None:
            tk.Label(container_frame, text="No issue to display",
                     font=("Arial", 12, "bold")).pack(pady=20)
            return

        row_counter = 0

        # Created by (reporter)
        created_by_text = f"Created by: {self.__issue.reporter.name}"
        tk.Label(container_frame, text=created_by_text, font=("Arial", 10, "bold")) \
            .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
        row_counter += 1

        # Updated by (updater)
        if self.__issue.updater and self.__issue.updater.name:
            updated_by_text = f"Updated by: {self.__issue.updater.name}"
            tk.Label(container_frame, text=updated_by_text, font=("Arial", 10, "bold")) \
                .grid(row=row_counter, column=0, sticky='ne', padx=(0, 5))
            row_counter += 1

        # Build the rest of the UI (summary, description, fields)
        self._build_summary_section(container_frame, row_counter)
        row_counter += 1
        self._build_description_section(container_frame, row_counter)
        row_counter += 1
        self._build_fields_section(container_frame, row_counter)

    def _build_summary_section(self, container: tk.Frame, row: int) -> None:
        summary_text = self.__issue.summary if self.__issue.summary else "No summary available"
        summary_text = summary_text[:100] + \
            "..." if len(summary_text) > 100 else summary_text
        tk.Label(container, text="Summary:", font=("Arial", 10, "bold")) \
            .grid(row=row, column=0, sticky='ne', padx=(0, 5))
        self.__summary_label = tk.Label(container, text=summary_text,
                                        font=("Arial", 10), wraplength=250, justify="left")
        self.__summary_label.grid(row=row, column=1, sticky='nw')

    def _build_description_section(self, container: tk.Frame, row: int) -> None:
        description_text = self.__issue.description if self.__issue.description else "No description available"
        description_text = description_text[:100] + "..." if len(
            description_text) > 100 else description_text
        tk.Label(container, text="Description:", font=("Arial", 10, "bold")) \
            .grid(row=row, column=0, sticky='ne', padx=(0, 5))
        self.__description_label = tk.Label(container, text=description_text,
                                            font=("Arial", 10), wraplength=250, justify="left")
        self.__description_label.grid(row=row, column=1, sticky='nw')

    def _build_fields_section(self, container: tk.Frame, start_row: int) -> None:
        row = start_row
        for field in self.__issue.fields:
            field_name = field.projectCustomField.field.name if field.projectCustomField.field else "Unknown Field"

            if isinstance(field.value, EnumBundleElement):
                field_value = field.value.name if field.value else "No value"
            elif isinstance(field.value, list):
                field_value = ", ".join(
                    [element.name for element in field.value if element.name]) if field.value else "No value"
            else:
                field_value = "No value"

            tk.Label(container, text=f"{field_name}:", font=("Arial", 10, "bold")) \
                .grid(row=row, column=0, sticky='ne', padx=(0, 5))
            self.__field_value_label = tk.Label(container, text=field_value,
                                                font=("Arial", 10), wraplength=250, justify="left")
            self.__field_value_label.grid(row=row, column=1, sticky='nw')
            row += 1
