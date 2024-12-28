import logging
import pyperclip
import pyautogui
import re

logger = logging.getLogger(__name__)


def get_number_from_clipboard(max_length: int = 10) -> str | None:
    """Get the selected number from the clipboard.

    Args:
        max_length (int, optional): The maximum length of the number to return. Defaults to 10.

    Returns:
        str | None: The selected number as a string, or None if no number is selected.
    """
    original = pyperclip.paste()
    pyperclip.copy("")

    pyautogui.hotkey("ctrl", "c")

    selected_text = pyperclip.paste()
    logger.info(f"Selected text: {selected_text}")

    pyperclip.copy(original)

    truncated_text = selected_text[:max_length] if selected_text else None
    return re.sub(r"[^\d]", "", truncated_text) if truncated_text else None
