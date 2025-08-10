import tkinter as tk
from tkinter import ttk
from typing import Optional
import logging

from models.custom_models import CustomIssue
from ui.views.base.custom_view import CustomView
from ui.views.base.custom_view_config import CustomViewConfig

logger = logging.getLogger(__name__)


class IssueViewerView(CustomView):
    def __init__(
        self,
        issue: Optional[CustomIssue] = None,
        config: Optional[CustomViewConfig] = None,
    ):
        super().__init__(config=config)
        self.__issue: Optional[CustomIssue] = issue

    def update_value(self, issue: Optional[CustomIssue] = None) -> None:
        """Update the view with new issue details."""
        self.__issue = issue
        self._build_ui()
        self.update_idletasks()
        self._flash_update(flash_color="red" if issue is None else "green")

    def _populate_widgets(self, parent: tk.Frame) -> None:
        parent.config(bg=self._config.bg_color)
        parent.grid_columnconfigure(0, weight=1)

        row = 0

        if self.__issue is None:
            label = tk.Label(
                parent,
                text="No issue to display",
                font=("Segoe UI", 12, "bold"),
                bg=self._config.bg_color,
                fg=self._config.text_color,
            )
            label.grid(row=row, column=0, pady=20, padx=10)
            return

        if self.__issue.reporter:
            created_by_text = f"Created by: {self.__issue.reporter.name}"
            self._add_label(parent, created_by_text, row)
            row += 1

        if self.__issue.updater and self.__issue.updater.name:
            updated_by_text = f"Updated by: {self.__issue.updater.name}"
            self._add_label(parent, updated_by_text, row)
            row += 1

        row = self._add_summary_section(parent, row)
        row = self._add_description_section(parent, row)

        if self.__issue.fields:
            self._add_fields_section(parent, row)

        if self.__issue.links:
            row = self._add_subtasks_section(parent, row)

    def _add_label(self, parent: tk.Frame, text: str, row: int) -> None:
        label = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=self._config.bg_color,
            fg=self._config.text_color,
        )
        label.grid(row=row, column=0, sticky="nw", padx=10, pady=5)

    def _add_summary_section(self, parent: tk.Frame, row: int) -> int:
        if not self.__issue or not self.__issue.summary:
            return row

        self._add_label(parent, "Summary:", row)
        row += 1

        return self._add_text_box(parent, self.__issue.summary, row, height=3)

    def _add_description_section(self, parent: tk.Frame, row: int) -> int:
        if not self.__issue or not self.__issue.description:
            return row

        self._add_label(parent, "Description:", row)
        row += 1

        return self._add_text_box(parent, self.__issue.description, row, height=5)

    def _add_text_box(
        self, parent: tk.Frame, text: str, row: int, height: int = 4
    ) -> int:
        """Add a scrollable text box."""
        frame = tk.Frame(parent, bg=self._config.bg_color)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        text_kwargs = {}
        if self._config.bg_color:
            text_kwargs["bg"] = self._config.bg_color
        if self._config.text_color:
            text_kwargs["fg"] = self._config.text_color
            text_kwargs["insertbackground"] = self._config.text_color
            text_kwargs["disabledforeground"] = self._config.text_color

        text_widget = tk.Text(
            frame,
            height=height,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            **text_kwargs,
        )
        text_widget.insert("1.0", text)
        text_widget.config(state=tk.DISABLED)

        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        scrollbar.config(command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

        return row + 1

    def _add_fields_section(self, parent: tk.Frame, row: int) -> None:
        self._add_label(parent, "Fields:", row)
        row += 1

        for field in self.__issue.fields:
            if not field.value:
                continue

            field_name = field.projectCustomField.field.name
            field_value = (
                field.value.name if hasattr(field.value, "name") else str(field.value)
            )

            field_frame = tk.Frame(parent, bg=self._config.bg_color)
            field_frame.grid(row=row, column=0, sticky="ew", padx=20, pady=2)
            field_frame.grid_columnconfigure(1, weight=1)
            row += 1

            field_label = tk.Label(
                field_frame,
                text=f"{field_name}:",
                font=("Segoe UI", 9, "bold"),
                bg=self._config.bg_color,
                fg=self._config.text_color,
            )
            field_label.grid(row=0, column=0, sticky="nw")

            value_label = tk.Label(
                field_frame,
                text=field_value,
                font=("Segoe UI", 9),
                bg=self._config.bg_color,
                fg=self._config.text_color,
            )
            value_label.grid(row=0, column=1, sticky="nw", padx=5)

    def _add_subtasks_section(self, parent: tk.Frame, row: int) -> int:
        if not hasattr(self.__issue, "links") or not self.__issue.links:
            return row

        subtask_texts = [
            f"{linked_issue.idReadable} - {linked_issue.summary}\n"
            for link in self.__issue.links
            if "subtask of" in link.linkType.targetToSource
            for linked_issue in link.trimmedIssues
        ]

        if not subtask_texts:
            return row

        frame = tk.Frame(parent, bg=self._config.bg_color)
        frame.grid(row=row, column=0, sticky="nsew", padx=10, pady=5)
        frame.grid_columnconfigure(0, weight=1)

        header_label = tk.Label(
            frame,
            text=f"Subtasks ({len(subtask_texts)}):",
            font=("Segoe UI", 10, "bold"),
            bg=self._config.bg_color,
        )
        header_label.grid(row=0, column=0, sticky="w")

        text_frame = tk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        v_scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal")

        text_kwargs = {"state": tk.DISABLED, "xscrollcommand": h_scrollbar.set, "yscrollcommand": v_scrollbar.set}
        if self._config.bg_color:
            text_kwargs["bg"] = self._config.bg_color
        if self._config.text_color:
            text_kwargs["fg"] = self._config.text_color
            text_kwargs["insertbackground"] = self._config.text_color
            text_kwargs["disabledforeground"] = self._config.text_color

        text_widget = tk.Text(
            text_frame,
            height=min(6, len(subtask_texts)),
            wrap=tk.NONE,
            font=("Segoe UI", 10),
            **text_kwargs,
        )
        text_widget.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        v_scrollbar.config(command=text_widget.yview)
        h_scrollbar.config(command=text_widget.xview)

        text_widget.config(state=tk.NORMAL)
        text_widget.insert("1.0", "".join(subtask_texts))
        text_widget.config(state=tk.DISABLED)

        return row + 1
