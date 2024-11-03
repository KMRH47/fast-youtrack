import traceback
import logging

from dependency_injector.wiring import Provide

from containers import Container
from logger.my_logger import setup_logger
from errors.user_error import UserError
from errors.user_cancelled_error import UserCancelledError
from ui.issue_view import IssueView
from ui.timer_view import TimerView
from ui.add_spent_time.add_spent_time_controller import AddSpentTimeController

setup_logger()


logger = logging.getLogger(__name__)


def main(
    add_spent_time_controller: AddSpentTimeController = Provide[
        Container.add_spent_time_controller],
    timer_view: TimerView = Provide[Container.timer_view],
    issue_view: IssueView = Provide[Container.issue_view]
) -> None:
    logger.info("Starting FastYouTrack...")

    add_spent_time_controller.set_issue_callback(issue_view.update_issue)
    add_spent_time_controller.get_window().attach_windows([
        (timer_view, "top"),
        (issue_view, "right")
    ])

    issue_id, add_spent_time_request = add_spent_time_controller.prompt()

    logger.info(f"Issue ID: {issue_id}")
    logger.info(f"Add Time Request: {add_spent_time_request}")


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
        logger.error(f'Unhandled exception\n{traceback.format_exc()}')
    finally:
        logging.shutdown()
