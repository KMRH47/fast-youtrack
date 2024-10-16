import logging
import os


def setup_logger(log_dir="logs", log_file="log.txt"):
    """
    Sets up logger configuration.
    Ensures log directory exists and logs to a file in the project root.
    """
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..'))
    log_dir = os.path.join(project_root, log_dir)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
