from datetime import date
from ui.custom.custom_view_config import CustomViewConfig


class AddSpentTimeWindowConfig(CustomViewConfig):
    project: str = ""
    issue_separator: str = "-"
    initial_issue_id: str = ""
    initial_time: str = ""
    initial_description: str = ""
    initial_type: str = ""
    work_item_types: dict[str, str] = {}
    date_format: str = "yyyy-mm-dd"
    initial_date: str = date.today().strftime(date_format)
