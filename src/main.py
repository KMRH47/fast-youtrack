import logging
import sys
from pathlib import Path

from dependency_injector.wiring import Provide

from containers import Container
from errors.user_cancelled_error import UserCancelledError
from errors.user_error import UserError
from config import Config
from app_args import AppArgs
from ui.windows.add_spent_time.add_spent_time_controller import AddSpentTimeController
from infrastructure import initialize_infrastructure
from utils.logging_utils import format_error_message
from utils.pid_utils import cleanup_pids_folder
from ui.splash import Splash

logger = logging.getLogger(__name__)


def main(
    add_spent_time_controller: AddSpentTimeController = Provide[
        Container.add_spent_time_controller
    ],
) -> None:
    logger.info("Starting FastYouTrack...")
    add_spent_time_controller.add_spent_time()


if __name__ == "__main__":
    splash = None
    try:
        splash = Splash()
        splash.show()
        args = AppArgs.from_sys_args()
        base_directory = Path(args.base_dir)
        config = Config.load_config(base_dir=base_directory)
        initialize_infrastructure(args, config)

        container = Container()
        container.args.override(args)
        container.config.override(config)
        container.init_resources()
        container.wire(modules=[__name__])
        if splash:
            splash.close()
        main()
    except UserCancelledError as e:
        if splash:
            splash.close()
        logger.info(f"Cancelled by user. {e}")
        sys.exit(0)
    except UserError as e:
        try:
            e.display()
        except Exception:
            logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        if splash:
            splash.close()
        error_details = format_error_message(e)
        logger.error(error_details)
    finally:
        cleanup_pids_folder()
        logging.shutdown()
