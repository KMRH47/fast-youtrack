import logging
import sys
import traceback
from logger.my_logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

try:
    import requests
    from repositories.file_manager import FileManager
    from services.http_service import HttpService
    from ui.add_spent_time.add_spent_time_view import AddSpentTimeView
    from ui.add_spent_time.add_spent_time_controller import AddSpentTimeController
    from errors.user_cancelled_error import UserCancelledError
    from errors.user_error import UserError
    from services.youtrack_service import YouTrackService
    from services.bearer_token_service import BearerTokenService
except Exception as e:
    logger.critical("Error during imports", exc_info=True)
    sys.exit(1)


def main():
    logger.info("Starting FastYouTrack...")
    passphrase = sys.argv[1] if len(sys.argv) > 1 else None
    subdomain = sys.argv[2] if len(sys.argv) > 2 else None

    if (not passphrase) or (not subdomain):
        raise ValueError("Passphrase and subdomain are required.")

    base_dir = f"../user/{subdomain}"

    token_service = BearerTokenService(
        base_dir=base_dir,
        passphrase=passphrase)

    bearer_token = token_service.get_bearer_token() or \
        token_service.prompt_for_bearer_token()

    http_service = HttpService(
        base_url=f"https://{subdomain}.youtrack.cloud/api",
        bearer_token=bearer_token
    )
    file_manager = FileManager(base_dir)
    youtrack_service = YouTrackService(
        http_service=http_service,
        file_manager=file_manager
    )

    issue_id, add_spent_time_request = AddSpentTimeController(
        AddSpentTimeView("DEMO-31"),
        youtrack_service).show()

    logger.info("Issue ID: " + issue_id)
    logger.info("Add Time Request: " + str(add_spent_time_request))

    # Test Updating Issue
    # logger.info(f"Updating issue {issue_id} with request:")
    # logger.info(issue_update_request)
    # youtrack_service.update_issue(issue_id, issue_update_request)


if __name__ == "__main__":
    try:
        main()
    except UserCancelledError as e:
        logger.info(f"Cancelled by user. {e}")
    except UserError as e:
        e.display()
    except requests.HTTPError as e:
        logger.error(f'HTTP error occurred: {e}')
    except Exception:
        logger.error(f'Unhandled exception\n{traceback.format_exc()}')
    finally:
        logging.shutdown()
