import logging
import sys


logger = logging.getLogger(__name__)

try:
    from ui.issue_view import IssueView
    from ui.timer_view import TimerView
    from ui.add_spent_time.add_spent_time_controller import AddSpentTimeController
    from ui.add_spent_time.add_spent_time_window import AddSpentTimeWindow
    from utils.clipboard import get_selected_number
    from config import (
        Config,
        load_config,
        create_issue_view_config,
        create_timer_view_config,
        create_add_spent_time_config,
        generate_bearer_token,
    )
    from dependency_injector import containers, providers
    from services.http_service import HttpService
    from services.youtrack_service import YouTrackService
    from repositories.file_manager import FileManager
    from services.bearer_token_service import BearerTokenService
    from security.encryption import EncryptionService
except Exception as e:
    logger.critical("Error during imports", exc_info=True)
    sys.exit(1)


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
        generate_bearer_token, bearer_token_service
    )

    http_service: providers.Provider[HttpService] = providers.Factory(
        HttpService,
        base_url=config().base_url,
        bearer_token=bearer_token,
    )

    youtrack_service: providers.Provider[YouTrackService] = providers.Singleton(
        YouTrackService,
        http_service=http_service,
        file_manager=file_manager,
    )

    issue_view_config = providers.Factory(
        create_issue_view_config,
    )

    timer_view_config = providers.Factory(
        create_timer_view_config,
    )

    add_spent_time_config = providers.Factory(
        create_add_spent_time_config,
        youtrack_service,
    )

    issue_view_factory = providers.Factory(
        IssueView,
        config=issue_view_config,
    )

    timer_view_factory = providers.Factory(
        TimerView,
        config=timer_view_config,
    )

    add_spent_time_window = providers.Singleton(
        AddSpentTimeWindow,
        issue_id=get_selected_number() or None,
        config=add_spent_time_config,
        attached_views=[issue_view_factory, timer_view_factory],
    )

    add_spent_time_controller = providers.Singleton(
        AddSpentTimeController,
        window=add_spent_time_window,
        youtrack_service=youtrack_service,
    )
