from logging.handlers import RotatingFileHandler
import os
import logging
from typing import Callable, Optional
from config import Config
from app_args import AppArgs
from macos_hotkey import maybe_register_ctrl_shift_t
from ui.windows.base.custom_window import CustomWindow


_stop_hotkey: Optional[Callable[[], None]] = None


def initialize_infrastructure(args: AppArgs, config: Config) -> None:
    """Initialize application infrastructure components"""
    initialize_logging(args, config)
    _initialize_hotkeys()


def shutdown_infrastructure() -> None:
    """Cleanly stop infrastructure subsystems (hotkeys, etc.)."""
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
        _stop_hotkey = maybe_register_ctrl_shift_t(CustomWindow.restore_app_to_front)


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
