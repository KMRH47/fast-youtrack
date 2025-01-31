from ui.views.base.custom_view_config import CustomViewConfig


class CustomWindowConfig(CustomViewConfig):
    title: str = "Untitled Window"
    minimize_to_tray: bool = True
