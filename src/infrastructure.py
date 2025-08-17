from logging.handlers import RotatingFileHandler
import os
import logging
from typing import Callable, Optional
from config import Config
from app_args import AppArgs
from macos_hotkey import maybe_register_ctrl_shift_t
from ui.windows.base.custom_window import CustomWindow
from ui.windows.add_spent_time.add_spent_time_window import AddSpentTimeWindow
from utils.clipboard import get_selected_text


_stop_hotkey: Optional[Callable[[], None]] = None


def initialize_infrastructure(args: AppArgs, config: Config) -> None:
    initialize_logging(args, config)
    _initialize_hotkeys()


def shutdown_infrastructure() -> None:
    global _stop_hotkey
    if _stop_hotkey:
        try:
            _stop_hotkey()
        except Exception:
            pass
        finally:
            _stop_hotkey = None


def _initialize_hotkeys() -> None:
    global _stop_hotkey
    if _stop_hotkey is None:
        _stop_hotkey = maybe_register_ctrl_shift_t(_on_hotkey_callback)


def _on_hotkey_callback() -> None:
    try:
        import tkinter as tk
        tk_root = getattr(tk, "_default_root", None)
        if tk_root is None:
            return
        selected_text = get_selected_text(initial_delay_s=0.25)

        def _apply():
            try:
                CustomWindow.restore_app_to_front()
                if isinstance(tk_root, AddSpentTimeWindow):
                    tk_root.handle_hotkey_activation(selected_text)
            except Exception:
                pass

        try:
            tk_root.after_idle(_apply)
        except Exception:
            _apply()
    except Exception:
        pass


def initialize_logging(args: AppArgs, config: Config) -> None:
    """Initialize logging configuration"""
    log_dir = os.path.join(args.base_dir, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.getLogger("PIL").setLevel(logging.INFO)

    logging.basicConfig(
        level=config.get_logging_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                filename=os.path.join(log_dir, "app.log"),
                maxBytes=args.max_log_size_bytes,
                backupCount=3,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )
