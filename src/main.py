from services.youtrack_service import YouTrackService
from logger.my_logger import setup_logger, log_uncaught_exceptions
from services.credentials_service import CredentialsService, handle_passphrase
from errors.invalid_passphrase_error import InvalidPassphraseError
import sys
import logging
import traceback


def main():
    passphrase = handle_passphrase(sys.argv[1] if len(sys.argv) > 1 else None)

    credentials_service = CredentialsService(passphrase)
    credentials = credentials_service.load_or_save_credentials(passphrase)
    
    youtrack_service = YouTrackService(
        credentials.subdomain, credentials.bearer_token)

    user_info = youtrack_service.get_user_info()

    logging.info(f"User info: {user_info}")


if __name__ == "__main__":
    try:
        setup_logger()
        sys.excepthook = log_uncaught_exceptions
        main()
    except InvalidPassphraseError as e:
        logging.error(e.message)
    except Exception as e:
        logging.error(f'Unhandled exception\n{traceback.format_exc()}')
