import sys
import logging
import traceback


try:
    from models.work_item_response import WorkItemResponse
    from services.youtrack_service import YouTrackService
    from logger.my_logger import setup_logger, log_uncaught_exceptions
    from services.credentials_service import CredentialsService, handle_passphrase
    from errors.invalid_passphrase_error import InvalidPassphraseError

    setup_logger()
    sys.excepthook = log_uncaught_exceptions

    try:
        passphrase = handle_passphrase(sys.argv[1] if len(sys.argv) > 1 else None)

        credentials_service = CredentialsService(passphrase)
        credentials = credentials_service.get_credentials()
        if not credentials:
            (subdomain, bearer_token) = credentials_service.prompt_token_and_subdomain(
                passphrase)
            youtrack_service = YouTrackService(subdomain, bearer_token)
            user_info: WorkItemResponse = youtrack_service.get_user_info()
            credentials_service.save_credentials(
                subdomain=subdomain,
                bearer_token=bearer_token,
                author_id=user_info.id,
                author_name=user_info.name)
        else:
            youtrack_service = YouTrackService(
                credentials.subdomain, credentials.bearer_token)

    except InvalidPassphraseError as e:
        logging.error(e.message)
    except Exception as e:
        logging.error(f'Unhandled exception\n{traceback.format_exc()}')

except Exception as e:
    logging.error(f'Unhandled exception\n{traceback.format_exc()}')
