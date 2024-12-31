from typing import Optional
from tkinter import ttk
import tkinter as tk
import logging

from services.youtrack_service import YouTrackService
from models.general_responses import Issue, StateBundleElement
from models.general_requests import IssueUpdateRequest, WorkItemField
from ui.views.base.custom_view_config import CustomViewConfig
from ui.views.base.custom_view import CustomView

logger = logging.getLogger(__name__)


class BundleEnums:
    STATE = "110-0"


class UpdateIssueView(CustomView):
    def __init__(
        self,
        youtrack_service: YouTrackService,
        config: Optional[CustomViewConfig] = None
    ):
        super().__init__(config=config)
        self.__youtrack_service = youtrack_service
        self.__issue: Optional[Issue] = None
        self.__issue_update_request: Optional[IssueUpdateRequest] = None
        self.selected_issue_state_var: Optional[tk.StringVar] = None
        self.issue_state_combobox: Optional[ttk.Combobox] = None

    def update_value(self, issue: Optional[Issue] = None) -> None:
        """Update the view with new issue details."""
        self.__issue = issue
        self._build_ui()
        self.update_idletasks()
        self._flash_update(flash_color="red" if issue is None else "green")

    def _populate_widgets(self, parent: tk.Frame) -> None:
        """Build the UI components."""
        parent.config(bg=self._config.bg_color)
        
        # Issue State ComboBox
        tk.Label(parent, text="Current State:", bg=self._config.bg_color).pack(anchor="w", padx=10)
        self.selected_issue_state_var = tk.StringVar()
        self.issue_state_combobox = ttk.Combobox(
            parent,
            values=self._get_available_issue_states(),
            textvariable=self.selected_issue_state_var,
        )
        self.issue_state_combobox.pack(anchor="w", padx=10, pady=5, fill="x", expand=True)
        
        # Bind events
        self.issue_state_combobox.bind("<<ComboboxSelected>>", self._on_issue_state_change)
        
        # Submit Button
        submit_button = tk.Button(
            parent, text="Update", command=self._on_submit, width=10
        )
        submit_button.pack(pady=5)

    def _get_available_issue_states(self) -> list[str]:
        """Get available issue states from YouTrack."""
        try:
            issue_states: list[StateBundleElement] = self.__youtrack_service.get_bundle(
                BundleEnums.STATE
            )
            return sorted([state.name for state in issue_states if state.name])
        except Exception as e:
            logger.error(f"Failed to get issue states: {e}")
            return []

    def _on_issue_state_change(self, _) -> None:
        """Handle state change in the combobox."""
        if not self._state_valid():
            self._apply_error_style(self.issue_state_combobox)
        else:
            self._reset_style(self.issue_state_combobox)

    def _state_valid(self) -> bool:
        """Validate the selected state."""
        current_state = self.selected_issue_state_var.get()
        return (
            not current_state
            or current_state in self.issue_state_combobox["values"]
        )

    def _apply_error_style(self, widget: ttk.Widget) -> None:
        """Apply error styling to a widget."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Error.TCombobox",
            fieldbackground="white",
            bordercolor="red",
            borderwidth=2
        )
        widget.config(style="Error.TCombobox")

    def _reset_style(self, widget: ttk.Widget) -> None:
        """Reset widget style to default."""
        widget.config(style="TCombobox")

    def _on_submit(self) -> None:
        """Handle form submission."""
        try:
            if not self.__issue:
                logger.error("No issue loaded")
                return

            current_state = self.selected_issue_state_var.get()
            if not current_state or not self._state_valid():
                return

            # Create field update for state change
            state_field = WorkItemField(
                name="State",
                value={"name": current_state}
            )

            self.__issue_update_request = IssueUpdateRequest(
                summary=self.__issue.summary,
                description=self.__issue.description,
                fields=[state_field],
                usesMarkdown=True
            )
            
            self.master.destroy()
        except Exception as e:
            logger.error(f"Error submitting issue update: {e}")
            self.master.destroy()
            raise
