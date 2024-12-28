import os
import logging
from config import Config
from app_args import AppArgs


def initialize_infrastructure(args: AppArgs, config: Config) -> None:
    """Initialize application infrastructure components"""
    initialize_logging(args, config)


def initialize_logging(args: AppArgs, config: Config) -> None:
    """Initialize logging configuration"""
    log_dir = os.path.join(args.base_dir, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=config.get_logging_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "app.log"), encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
