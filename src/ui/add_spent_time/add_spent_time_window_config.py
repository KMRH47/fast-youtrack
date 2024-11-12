from ui.custom.custom_view_config import CustomViewConfig


class AddSpentTimeWindowConfig(CustomViewConfig):
    project: str = ""
    issue_separator: str = "-"
    initial_issue_id: str = ""
    initial_time: str = ""
    initial_description: str = ""
    initial_type: str = ""
    date_format: str = "%d-%m-%Y"
