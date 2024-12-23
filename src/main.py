import traceback
import logging

from dependency_injector.wiring import Provide

from containers import Container
from logger.my_logger import setup_logger
from errors.user_error import UserError
from errors.user_cancelled_error import UserCancelledError
from ui.windows.add_spent_time.add_spent_time_controller import AddSpentTimeController

setup_logger()


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
        container = Container()
        container.init_resources()
        container.wire(modules=[__name__])
        main()
    except UserCancelledError as e:
        logger.info(f"Cancelled by user. {e}")
    except UserError as e:
        e.display()
    except Exception:
        logger.error(f"Unhandled exception\n{traceback.format_exc()}")
    finally:
        logging.shutdown()
