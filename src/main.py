from requests import HTTPError
from services.youtrack_service import YouTrackService
from logger.my_logger import setup_logger
from services.bearer_token_service import BearerTokenService
from errors.invalid_passphrase_error import InvalidPassphraseError
from errors.invalid_token_error import InvalidTokenError
import sys
import logging
import traceback


logger = logging.getLogger(__name__)


def main():
    passphrase = sys.argv[1] if len(sys.argv) > 1 else None
    subdomain = sys.argv[2] if len(sys.argv) > 2 else None

    token_service = BearerTokenService(
        base_path=f"../user/{subdomain}",
        passphrase=passphrase)

    youtrack_service = YouTrackService(
        subdomain=subdomain,
        bearer_token=token_service.get_bearer_token() or token_service.prompt_for_bearer_token())

    work_item_types = youtrack_service.get_work_item_types()

    logger.info(f"Work Item Types (test): {work_item_types}")


if __name__ == "__main__":
    try:
        setup_logger()
        main()
    except (InvalidPassphraseError, InvalidTokenError, HTTPError) as e:
        logger.error(e.message)
    except Exception as e:
        logger.error(f'Unhandled exception\n{traceback.format_exc()}')
