import logging

from dependency_injector.wiring import Provide

from containers import Container
from config import load_config
from errors.user_error import UserError
from errors.user_cancelled_error import UserCancelledError
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
        config = load_config()
        initialize_infrastructure(config)

        container = Container()
        container.init_resources()
        container.wire(modules=[__name__])
        main()
    except UserCancelledError as e:
        if logging.getLogger().handlers:
            logger.info(f"Cancelled by user. {e}")
        raise
    except UserError as e:
        e.display()
    except Exception as e:
        error_details = format_error_message(e)
        if logging.getLogger().handlers:
            logger.error(error_details)
        UserError(error_details).display()
    finally:
        logging.shutdown()
