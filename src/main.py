from ui.youtrack_story_update_ui import display_youtrack_story_update
from errors.user_error import UserError
from requests import HTTPError
from services.youtrack_service import YouTrackService
from logger.my_logger import setup_logger
from services.bearer_token_service import BearerTokenService
import sys
import logging
import traceback


logger = logging.getLogger(__name__)


def main():
    passphrase = sys.argv[1] if len(sys.argv) > 1 else None
    subdomain = sys.argv[2] if len(sys.argv) > 2 else None

    if (not passphrase) or (not subdomain):
        raise ValueError("Passphrase and subdomain are required.")

    token_service = BearerTokenService(
        base_path=f"../user/{subdomain}",
        passphrase=passphrase)

    youtrack_service = YouTrackService(
        subdomain=subdomain,
        bearer_token=token_service.get_bearer_token() or token_service.prompt_for_bearer_token())

    #work_item_types =  youtrack_service.get_work_item_types()
    #display_youtrack_story_update(available_states=[item.name for item in work_item_types])
    test_list = ['testing', 'haha', 'okay']
    display_youtrack_story_update(available_states=test_list)

    # logger.info(f"Work Item Types (test): {work_item_types}")


if __name__ == "__main__":
    try:
        setup_logger()
        main()
    except UserError as e:
        e.display()
    except HTTPError as e:
        logger.error(e.response.text)
    except Exception as e:
        logger.error(f'Unhandled exception\n{traceback.format_exc()}')
