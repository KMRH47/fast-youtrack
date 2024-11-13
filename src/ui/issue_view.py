import tkinter as tk
from typing import Optional
import logging

from models.general_responses import EnumBundleElement, Issue
from ui.custom.custom_view_config import CustomViewConfig
from ui.custom.custom_view import CustomView

logger = logging.getLogger(__name__)


class IssueView(CustomView):
    __issue: Optional[Issue] = None

    def __init__(
        self, issue: Optional[Issue] = None, config: Optional[CustomViewConfig] = None
    ):
        super().__init__(config=config)
        self.__issue = issue

    def update_value(self, issue: Optional[Issue] = None) -> None:
        """Update the window with new issue details."""
        self.__issue = issue

        self._build_ui()
        self.update_idletasks()
        self._flash_update(flash_color="red" if issue is None else "green")

    def _populate_widgets(self, parent: tk.Frame) -> None:
        """Populate widgets into the parent frame with issue details."""
        row = 0

        if self.__issue is None:
            label = tk.Label(
                parent, text="No issue to display", font=("Arial", 12, "bold")
            )
            label.grid(row=row, column=0, pady=20)
            return

        created_by_text = f"Created by: {self.__issue.reporter.name}"
        created_by_label = tk.Label(
            parent, text=created_by_text, font=("Arial", 10, "bold")
        )
        created_by_label.grid(row=row, column=0, sticky="ne", padx=(0, 5))
        row += 1

        if self.__issue.updater and self.__issue.updater.name:
            updated_by_text = f"Updated by: {self.__issue.updater.name}"
            updated_by_label = tk.Label(
                parent, text=updated_by_text, font=("Arial", 10, "bold")
            )
            updated_by_label.grid(row=row, column=0, sticky="ne", padx=(0, 5))
            row += 1

        row = self._add_summary_section(parent, row)
        row = self._add_description_section(parent, row)

        self._add_fields_section(parent, row)

    def _add_summary_section(self, parent: tk.Frame, row: int) -> int:
        """Add the summary section to the parent and return updated row."""
        summary_text = self.__issue.summary or "No summary available"
        summary_text = (
            (summary_text[:100] + "...") if len(summary_text) > 100 else summary_text
        )

        label = tk.Label(parent, text="Summary:", font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, sticky="ne", padx=(0, 5))

        summary_label = tk.Label(
            parent,
            text=summary_text,
            font=("Arial", 10),
            wraplength=250,
            justify="left",
        )
        summary_label.grid(row=row, column=1, sticky="nw")

        return row + 1

    def _add_description_section(self, parent: tk.Frame, row: int) -> int:
        """Add the description section to the parent and return updated row."""
        description_text = self.__issue.description or "No description available"
        description_text = (
            (description_text[:100] + "...")
            if len(description_text) > 100
            else description_text
        )

        label = tk.Label(parent, text="Description:", font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, sticky="ne", padx=(0, 5))

        description_label = tk.Label(
            parent,
            text=description_text,
            font=("Arial", 10),
            wraplength=250,
            justify="left",
        )
        description_label.grid(row=row, column=1, sticky="nw")

        return row + 1

    def _add_fields_section(self, parent: tk.Frame, start_row: int) -> None:
        """Add field labels for each custom field in the issue."""
        row = start_row
        for field in self.__issue.fields:
            field_name = (
                field.projectCustomField.field.name
                if field.projectCustomField.field
                else "Unknown Field"
            )

            if isinstance(field.value, EnumBundleElement):
                field_value = field.value.name if field.value else "No value"
            elif isinstance(field.value, list):
                if all(isinstance(element, dict) for element in field.value):
                    field_value = ", ".join(
                        [element.get("name", "No name") for element in field.value]
                    )
                else:
                    field_value = (
                        ", ".join(
                            [
                                element.name
                                for element in field.value
                                if hasattr(element, "name")
                            ]
                        )
                        if field.value
                        else "No value"
                    )
            elif isinstance(field.value, dict):
                field_value = field.value.get("name", "No name")
            else:
                field_value = "No value"

            field_label = tk.Label(
                parent, text=f"{field_name}:", font=("Arial", 10, "bold")
            )
            field_label.grid(row=row, column=0, sticky="ne", padx=(0, 5))

            value_label = tk.Label(
                parent,
                text=field_value,
                font=("Arial", 10),
                wraplength=250,
                justify="left",
            )
            value_label.grid(row=row, column=1, sticky="nw")

            row += 1
