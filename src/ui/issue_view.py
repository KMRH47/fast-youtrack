import tkinter as tk
from typing import Optional
import logging

from models.general_responses import EnumBundleElement, Issue
from ui.custom.custom_window_config import CustomWindowConfig
from ui.custom.custom_toplevel import CustomTopLevel

logger = logging.getLogger(__name__)


class IssueView(CustomTopLevel):
    def __init__(self, issue: Optional[Issue] = None, config: Optional[CustomWindowConfig] = None):
        super().__init__(config)
        self.__issue = issue

    def update_issue(self, issue: Issue) -> None:
        """Update the window with new issue details."""
        self.__issue = issue

        if self.get_window():
            self._build_ui()
            self.get_window().update_idletasks()
            self.get_window().geometry("")

    def _build_ui(self) -> None:
        """Build the UI for displaying issue details."""
        window = self.get_window()
        if not window:
            return

        self._clear_window(window)

        container_frame = tk.Frame(window, padx=10, pady=10)
        container_frame.pack(fill='both', expand=True)

        self._populate_widgets(container_frame)

    def _clear_window(self, window: tk.Tk) -> None:
        """Destroy all child widgets of the given window."""
        for widget in window.winfo_children():
            widget.destroy()

    def _populate_widgets(self, parent: tk.Frame) -> None:
        """Populate widgets into the parent frame with issue details."""
        row = 0

        if self.__issue is None:
            label = tk.Label(parent, text="No issue to display",
                             font=("Arial", 12, "bold"))
            label.grid(row=row, column=0, pady=20)
            return

        created_by_text = f"Created by: {self.__issue.reporter.name}"
        created_by_label = tk.Label(
            parent, text=created_by_text, font=("Arial", 10, "bold"))
        created_by_label.grid(row=row, column=0, sticky='ne', padx=(0, 5))
        row += 1

        if self.__issue.updater and self.__issue.updater.name:
            updated_by_text = f"Updated by: {self.__issue.updater.name}"
            updated_by_label = tk.Label(
                parent, text=updated_by_text, font=("Arial", 10, "bold"))
            updated_by_label.grid(row=row, column=0, sticky='ne', padx=(0, 5))
            row += 1

        row = self._add_summary_section(parent, row)
        row = self._add_description_section(parent, row)

        # Fields section
        self._add_fields_section(parent, row)

    def _add_summary_section(self, parent: tk.Frame, row: int) -> int:
        """Add the summary section to the parent and return updated row."""
        summary_text = self.__issue.summary or "No summary available"
        summary_text = (
            summary_text[:100] + "...") if len(summary_text) > 100 else summary_text

        label = tk.Label(parent, text="Summary:", font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, sticky='ne', padx=(0, 5))

        summary_label = tk.Label(
            parent,
            text=summary_text,
            font=("Arial", 10),
            wraplength=300,
            justify="left"
        )
        summary_label.grid(row=row, column=1, sticky='nw')

        return row + 1

    def _add_description_section(self, parent: tk.Frame, row: int) -> int:
        """Add the description section to the parent and return updated row."""
        description_text = self.__issue.description or "No description available"
        description_text = (
            description_text[:100] + "...") if len(description_text) > 100 else description_text

        label = tk.Label(parent, text="Description:",
                         font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, sticky='ne', padx=(0, 5))

        description_label = tk.Label(
            parent,
            text=description_text,
            font=("Arial", 10),
            wraplength=250,
            justify="left"
        )
        description_label.grid(row=row, column=1, sticky='nw')

        return row + 1

    def _add_fields_section(self, parent: tk.Frame, start_row: int) -> None:
        """Add field labels for each custom field in the issue."""
        row = start_row
        for field in self.__issue.fields:
            field_name = field.projectCustomField.field.name if field.projectCustomField.field else "Unknown Field"

            if isinstance(field.value, EnumBundleElement):
                field_value = field.value.name if field.value else "No value"
            elif isinstance(field.value, list):
                field_value = ", ".join(
                    [element.name for element in field.value if element.name]
                ) if field.value else "No value"
            else:
                field_value = "No value"

            field_label = tk.Label(
                parent, text=f"{field_name}:", font=("Arial", 10, "bold"))
            field_label.grid(row=row, column=0, sticky='ne', padx=(0, 5))

            value_label = tk.Label(
                parent,
                text=field_value,
                font=("Arial", 10),
                wraplength=250,
                justify="left"
            )
            value_label.grid(row=row, column=1, sticky='nw')

            row += 1
