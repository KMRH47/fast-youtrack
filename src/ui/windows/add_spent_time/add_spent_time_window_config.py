from datetime import date

from ui.views.base.custom_window_config import CustomWindowConfig
from ui.widgets.custom_date_entry import CustomDateEntry


class AddSpentTimeWindowConfig(CustomWindowConfig):
    width: int = 300
    height: int = 325
    title: str = "Add Spent Time"
    cancel_key: str = "Escape"
    submit_key: str = "Return"
    project: str = ""
    issue_separator: str = "-"
    initial_issue_id: str = ""
    initial_time: str = ""
    initial_description: str = ""
    initial_type: str = ""
    work_item_types: dict[str, str] = {}
    date_format: str = "yyyy-mm-dd"
    
    @property
    def initial_date(self) -> str:
        python_format = CustomDateEntry.DATE_FORMAT_MAP.get(self.date_format.lower(), "%Y-%m-%d")
        return date.today().strftime(python_format)
