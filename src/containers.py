from ui.windows.add_spent_time.add_spent_time_controller import (
    AddSpentTimeController,
)
from ui.windows.add_spent_time.add_spent_time_window import AddSpentTimeWindow
from ui.views.issue_viewer.issue_viewer_view import IssueViewerView
from ui.views.timer.timer_view import TimerView
from utils.clipboard import get_number_from_clipboard
from config import Config, load_config
from dependency_injector import containers, providers
from services.youtrack_service import YouTrackService
from stores.file_store import FileStore
from services.bearer_token_service import BearerTokenService
from security.encryption import EncryptionService
from common.storage.store import Store
from stores.config_store import ConfigStore
from services.http.youtrack_http_client import YouTrackHttpClient


class Container(containers.DeclarativeContainer):
    config_values: Config = load_config()
    config = providers.Object(config_values)

    store: providers.Provider[Store] = providers.Singleton(
        FileStore,
        base_dir=config().base_dir,
    )

    config_store: providers.Provider[ConfigStore] = providers.Singleton(
        ConfigStore,
        store=store,
    )

    encryption_service: providers.Provider[EncryptionService] = providers.Factory(
        EncryptionService,
        passphrase=config().passphrase,
    )

    bearer_token_service: providers.Provider[BearerTokenService] = providers.Factory(
        BearerTokenService,
        store=store,
        encryption_service=encryption_service,
        token_file_name=config().token_file_name,
    )

    youtrack_http_client = providers.Factory(
        YouTrackHttpClient,
        base_url=config().base_url,
        bearer_token_service=bearer_token_service,
        config_store=config_store,
    )

    youtrack_service: providers.Provider[YouTrackService] = providers.Singleton(
        YouTrackService,
        http_client=youtrack_http_client,
        store=store,
    )

    issue_view_factory = providers.Factory(
        IssueViewerView,
        config=providers.Callable(lambda config=config().issue_view_config: config),
    )

    timer_view_factory = providers.Factory(
        TimerView,
        config=providers.Callable(lambda config=config().timer_view_config: config),
    )

    add_spent_time_config = providers.Factory(
        lambda config, youtrack_service: config.add_spent_time_config.copy(
            update={
                "work_item_types": config.add_spent_time_config.work_item_types
                or {
                    item.name: item.id
                    for item in youtrack_service.get_work_item_types()
                }
            }
        ),
        config,
        youtrack_service,
    )

    add_spent_time_window = providers.Singleton(
        AddSpentTimeWindow,
        issue_id=get_number_from_clipboard() or None,
        config=add_spent_time_config,
        attached_views=[issue_view_factory, timer_view_factory],
    )

    add_spent_time_controller = providers.Singleton(
        AddSpentTimeController,
        window=add_spent_time_window,
        youtrack_service=youtrack_service,
    )
