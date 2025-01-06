import logging
import sys

from dependency_injector.wiring import Provide

from containers import Container
from errors.user_error import UserError
from errors.user_cancelled_error import UserCancelledError
from config import Config
from app_args import AppArgs
from utils.clipboard import get_number_from_clipboard
from ui.windows.add_spent_time.add_spent_time_controller import AddSpentTimeController
from infrastructure import initialize_infrastructure
from utils.logging_utils import format_error_message

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
        if logging.getLogger().handlers:
            logger.info(f"Cancelled by user. {e}")
        sys.exit(0)
    except UserError as e:
        e.display()
    except Exception as e:
        error_details = format_error_message(e)
        if logging.getLogger().handlers:
            logger.error(error_details)
        UserError(error_details).display()
    finally:
        logging.shutdown()
