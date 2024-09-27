from services.youtrack_service import YouTrackService
from logger.my_logger import setup_logger
from services.credentials_service import CredentialsService, handle_passphrase
from errors.invalid_passphrase_error import InvalidPassphraseError
from errors.invalid_token_error import InvalidTokenError
import sys
import logging
import traceback


logger = logging.getLogger(__name__)


def main():
    passphrase = handle_passphrase(sys.argv[1] if len(sys.argv) > 1 else None)

    credentials_service = CredentialsService(passphrase)
    credentials = credentials_service.load_or_save_credentials(passphrase)

    youtrack_service = YouTrackService(
        credentials.subdomain, credentials.bearer_token)

    user_info = youtrack_service.get_user_info()

    logger.info(f"User info: {user_info}")


if __name__ == "__main__":
    try:
        setup_logger()
        main()
    except (InvalidPassphraseError, InvalidTokenError) as e:
        logger.error(e.message)
    except Exception as e:
        logger.error(f'Unhandled exception\n{traceback.format_exc()}')
