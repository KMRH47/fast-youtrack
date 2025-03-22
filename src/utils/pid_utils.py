import os
import shutil
import logging

logger = logging.getLogger(__name__)


def cleanup_pids_folder():
    """Delete the pids folder in the root directory"""
    try:
        pids_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), "pids")
        if os.path.exists(pids_dir):
            logger.info(f"Cleaning up pids folder: {pids_dir}")
            shutil.rmtree(pids_dir)
    except Exception as e:
        logger.error(f"Error cleaning up pids folder: {e}")
