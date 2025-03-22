import logging
import sys

from dependency_injector.wiring import Provide

from containers import Container
from errors.user_cancelled_error import UserCancelledError
from config import Config
from app_args import AppArgs
from ui.windows.add_spent_time.add_spent_time_controller import AddSpentTimeController
from infrastructure import initialize_infrastructure
from utils.logging_utils import format_error_message
from utils.pid_utils import cleanup_pids_folder

logger = logging.getLogger(__name__)


def main(
    add_spent_time_controller: AddSpentTimeController = Provide[
        Container.add_spent_time_controller
    ],
) -> None:
    logger.info("Starting FastYouTrack...")
    add_spent_time_controller.add_spent_time()


if __name__ == "__main__":
    try:
        args = AppArgs.from_sys_args()
        config = Config.load_config()
        initialize_infrastructure(args, config)

        container = Container()
        container.args.override(args)
        container.config.override(config)
        container.init_resources()
        container.wire(modules=[__name__])
        main()
    except UserCancelledError as e:
        logger.info(f"Cancelled by user. {e}")
        sys.exit(0)
    except Exception as e:
        error_details = format_error_message(e)
        logger.error(error_details)
    finally:
        cleanup_pids_folder()
        logging.shutdown()
