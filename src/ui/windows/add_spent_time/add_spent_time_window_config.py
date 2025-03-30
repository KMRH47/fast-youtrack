from datetime import date

from ui.views.base.custom_window_config import CustomWindowConfig


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
    date_format: str = "%Y-%m-%d"
    initial_date: str = date.today().strftime(date_format)
