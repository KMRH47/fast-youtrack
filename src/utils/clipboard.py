import logging
import pyperclip
import pyautogui
import re
import platform
import time

logger = logging.getLogger(__name__)


def get_number_from_clipboard(max_length: int = 10) -> str:
    """Get the selected number from the clipboard.

    Args:
        max_length (int, optional): The maximum length of the number to return. Defaults to 10.

    Returns:
        str: The selected number as a string, or empty string if no number is selected.
    """
    original = pyperclip.paste()
    pyperclip.copy("")
    pyautogui.hotkey("ctrl", "c")
    selected_text = pyperclip.paste()
    pyperclip.copy(original)
    truncated_text = selected_text[:max_length] if selected_text else ""
    return re.sub(r"[^\d]", "", truncated_text)


def get_selected_text(max_length: int = 64, initial_delay_s: float = 0.25) -> str:
    """Copy and return current selection without clobbering clipboard."""
    try:
        original_clipboard = pyperclip.paste()
    except Exception:
        original_clipboard = ""

    selected_text = ""
    modifier = "command" if platform.system() == "Darwin" else "ctrl"

    if initial_delay_s and initial_delay_s > 0:
        time.sleep(initial_delay_s)

    for delay in (0.0, 0.12, 0.25):
        try:
            pyautogui.hotkey(modifier, "c")
        except Exception:
            break
        if delay:
            time.sleep(delay)
        try:
            selected_text = pyperclip.paste()
        except Exception:
            selected_text = ""
        if selected_text:
            break

    try:
        pyperclip.copy(original_clipboard)
    except Exception:
        pass

    if not selected_text:
        return ""
    return selected_text.strip()[:max_length]
