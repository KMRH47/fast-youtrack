from config import Config
from ui.windows.add_spent_time.add_spent_time_controller import (
    AddSpentTimeController,
)
from ui.windows.add_spent_time.add_spent_time_window import AddSpentTimeWindow
from ui.views.issue_viewer.issue_viewer_view import IssueViewerView
from ui.views.timer.timer_view import TimerView
from dependency_injector import containers, providers
from services.youtrack_service import YouTrackService
from stores.file_store import FileStore
from services.bearer_token_service import BearerTokenService
from security.encryption import EncryptionService
from stores.store import Store
from stores.config_store import ConfigStore
from services.http.youtrack_http_client import YouTrackHttpClient
from app_args import AppArgs


class Container(containers.DeclarativeContainer):
    args = providers.Dependency(AppArgs)
    config = providers.Singleton(Config)

    store: providers.Provider[Store] = providers.Singleton(
        FileStore,
        base_dir=args.provided.base_dir,
    )

    config_store: providers.Provider[ConfigStore] = providers.Singleton(
        ConfigStore,
        store=store,
    )

    encryption_service: providers.Provider[EncryptionService] = providers.Factory(
        EncryptionService,
        passphrase=args.provided.passphrase,
    )

    bearer_token_service: providers.Provider[BearerTokenService] = providers.Factory(
        BearerTokenService,
        store=store,
        encryption_service=encryption_service,
        token_file_name=config.provided.token_file_name,
    )

    youtrack_http_client = providers.Factory(
        YouTrackHttpClient,
        base_url=args.provided.base_url,
        bearer_token_service=bearer_token_service,
        config_store=config_store,
    )

    youtrack_service: providers.Provider[YouTrackService] = providers.Singleton(
        YouTrackService,
        http_client=youtrack_http_client,
        store=store,
    )

    issue_view_factory: providers.Provider[IssueViewerView] = providers.Factory(
        IssueViewerView,
        config=config.provided.issue_view_config,
    )

    timer_view_factory: providers.Provider[TimerView] = providers.Factory(
        TimerView,
        config=config.provided.timer_view_config,
    )

    add_spent_time_config = providers.Factory(
        lambda config: config.add_spent_time_config.copy(),
        config,
    )

    add_spent_time_window = providers.Singleton(
        AddSpentTimeWindow,
        config=add_spent_time_config,
        attached_views=[issue_view_factory, timer_view_factory],
    )

    add_spent_time_controller = providers.Singleton(
        AddSpentTimeController,
        window=add_spent_time_window,
        youtrack_service=youtrack_service,
    )
