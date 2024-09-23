import sys
import logging


try:
    from models.work_item_response import WorkItemResponse
    from services.youtrack_service import YouTrackService
    from logger.my_logger import setup_logger, log_uncaught_exceptions
    from repositories.credentials_storage import write_passphrase, read_passphrase
    from services.credentials_service import CredentialsService

    setup_logger()
    sys.excepthook = log_uncaught_exceptions

    try:
        passphrase = sys.argv[1] if len(sys.argv) > 1 else None

        if not passphrase:
            passphrase = read_passphrase()
            if not passphrase:
                logging.error("No passphrase supplied. Exiting...")
                sys.exit(1)
        else:
            write_passphrase(passphrase)

        credentials_service = CredentialsService(passphrase)
        credentials = credentials_service.get_credentials()
        if not credentials:
            (subdomain, bearer_token) = credentials_service.prompt_token_and_subdomain(
                passphrase)
            youtrack_service = YouTrackService(subdomain, bearer_token)
            user_info: WorkItemResponse = youtrack_service.get_user_info()
            credentials_service.save_credentials(
                subdomain, bearer_token, user_info.id, user_info.name)
        else:
            youtrack_service = YouTrackService(
                credentials.subdomain, credentials.bearer_token)

        youtrack_service.get_user_info()

    except Exception as e:
        logging.error(f"An error occurred during execution: {e}")

except Exception as e:
    logging.error(
        f"Failed to import required modules or other initialization error: {e}")
