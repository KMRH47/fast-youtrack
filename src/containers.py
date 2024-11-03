import logging
import sys


logger = logging.getLogger(__name__)

try:
    from ui.custom.custom_window import CustomWindow
    from ui.issue_view import IssueView
    from ui.timer_view import TimerView
    from ui.add_spent_time.add_spent_time_controller import AddSpentTimeController
    from ui.add_spent_time.add_spent_time_view import AddSpentTimeView
    from config import Config, load_config
    from dependency_injector import containers, providers
    from services.http_service import HttpService
    from services.youtrack_service import YouTrackService
    from repositories.file_manager import FileManager
    from services.bearer_token_service import BearerTokenService
    from security.encryption import EncryptionService
except Exception as e:
    logger.critical("Error during imports", exc_info=True)
    sys.exit(1)


def generate_bearer_token(service: BearerTokenService) -> str:
    return service.get_bearer_token() or service.prompt_for_bearer_token()


class Container(containers.DeclarativeContainer):

    config_values: Config = load_config()
    config = providers.Object(config_values)

    file_manager: providers.Provider[FileManager] = providers.Factory(
        FileManager,
        base_dir=config().base_dir,
    )

    encryption_service: providers.Provider[EncryptionService] = providers.Factory(
        EncryptionService,
        passphrase=config().passphrase,
    )

    bearer_token_service: providers.Provider[BearerTokenService] = providers.Factory(
        BearerTokenService,
        file_manager=file_manager,
        encryption_service=encryption_service,
        token_file_name=config().token_file_name,
    )

    bearer_token: providers.Provider[str] = providers.Callable(
        generate_bearer_token,
        bearer_token_service
    )

    http_service: providers.Provider[HttpService] = providers.Factory(
        HttpService,
        base_url=config().base_url,
        bearer_token=bearer_token,
    )

    youtrack_service: providers.Provider[YouTrackService] = providers.Factory(
        YouTrackService,
        http_service=http_service,
        file_manager=file_manager,
    )

    custom_window: providers.Provider[CustomWindow] = providers.Factory(
        CustomWindow,
        config=providers.Object(config().add_spent_time_config)
    )

    clipboard = "DEMO-31"

    add_spent_time_view: providers.Provider[AddSpentTimeView] = providers.Factory(
        AddSpentTimeView,
        window=custom_window,
        issue_id=clipboard or None
    )

    add_spent_time_controller: providers.Provider[AddSpentTimeController] = providers.Factory(
        AddSpentTimeController,
        view=add_spent_time_view,
        youtrack_service=youtrack_service
    )

    issue_view: providers.Provider[IssueView] = providers.Factory(
        IssueView,
        config=providers.Object(config().issue_view_config)
    )

    timer_view: providers.Provider[TimerView] = providers.Factory(
        TimerView,
        config=providers.Object(config().timer_view_config)
    )
