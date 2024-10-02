import logging
import time
import pyperclip
import pyautogui
import re

logger = logging.getLogger(__name__)


def get_selected_number(max_length: int = 10) -> str | None:
    # Clear the clipboard
    pyperclip.copy('')

    # Simulate 'Ctrl+C' to copy the selected text to the clipboard
    pyautogui.hotkey('ctrl', 'c')

    # Wait briefly to ensure the clipboard is updated
    time.sleep(0.1)

    # Get the copied text from the clipboard
    selected_text = pyperclip.paste()

    # Truncate the selected text to the maximum length
    truncated_text = selected_text[:max_length] if selected_text else None

    # Extract and return digits from the truncated text, if any
    return re.sub(r'[^\d]', '', truncated_text) if truncated_text else None
