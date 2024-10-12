import sys
import logging
import traceback

from errors.user_cancelled_error import UserCancelledError
from ui.update_youtrack_issue_ui import IssueUpdateRequestUI
from errors.user_error import UserError
from services.youtrack_service import YouTrackService
from logger.my_logger import setup_logger
from services.bearer_token_service import BearerTokenService


logger = logging.getLogger(__name__)


def main():
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

    youtrack_service = YouTrackService(
        subdomain=subdomain,
        bearer_token=bearer_token,
        base_dir=base_dir)

    issue_update_ui = IssueUpdateRequestUI(youtrack_service)

    # Test Updating Issue
    issue_update_request = issue_update_ui.prompt("DEMO-31")

    logger.info(issue_update_request)

    # youtrack_service.update_issue(issue_id, issue_update_request)


if __name__ == "__main__":
    try:
        setup_logger()
        main()
    except UserCancelledError as e:
        logger.info(f"Cancelled by user. {e}")
    except UserError as e:
        e.display()
    except Exception as e:
        logger.error(f'Unhandled exception\n{traceback.format_exc()}')
    finally:
        logging.shutdown()
