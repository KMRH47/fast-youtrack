from models.story_update import StoryState, StoryUpdate
from utils.clipboard import get_selected_number
from ui.update_youtrack_story_ui import display_update_youtrack_story_ui
from errors.user_error import UserError
from requests import HTTPError
from services.youtrack_service import YouTrackService
from logger.my_logger import setup_logger
from services.bearer_token_service import BearerTokenService
import sys
import logging
import traceback


logger = logging.getLogger(__name__)


def update_youtrack_story_test(story_update: StoryUpdate) -> None:
    try:
        logger.info("Updating YouTrack story")
        logger.info(f"Story update: {story_update}")
    except Exception as e:
        logger.error(f"Exception occurred: {e}")


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

    work_item_types = youtrack_service.get_work_item_types()
    story_update = StoryUpdate(
        issue_id=f"AGI-{get_selected_number() or ''}",
        state=StoryState(available_states=[item.name for item in work_item_types]))

    display_update_youtrack_story_ui(story_update,
                                     on_ok_clicked=lambda story_update: update_youtrack_story_test(story_update))


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
