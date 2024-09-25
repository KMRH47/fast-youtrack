import sys
import logging
import os

class StreamToLogger:
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.ERROR):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    # This is required for `sys.stderr` replacement
    def flush(self):
        pass

def setup_logger(log_dir="logs", log_file="log.txt"):
    """
    Sets up logger configuration. Ensures log directory exists and logs to a file in the project root.
    """
    # Get the absolute path to the project root (two levels up from src/main.py)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    log_dir = os.path.join(project_root, log_dir)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, log_file)
    
    logging.basicConfig(
        filename=log_path,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        encoding='utf-8'
    )

    sys.stderr = StreamToLogger(logging.getLogger(), logging.ERROR)


def log_uncaught_exceptions(exctype, value, tb):
    """
    Logs any uncaught exceptions that occur during runtime.
    """
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))
