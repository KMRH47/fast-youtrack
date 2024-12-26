import logging
from typing import Optional

from security.encryption import EncryptionService
from errors.user_cancelled_error import UserCancelledError
from common.storage.store import Store
from ui.token_ui import display_bearer_token_prompt


logger = logging.getLogger(__name__)


class BearerTokenService:
    def __init__(
        self, store: Store, encryption_service: EncryptionService, token_file_name: str
    ):
        self._store = store
        self._encryption_service = encryption_service
        self._token_file_name = token_file_name

    def get_bearer_token(self) -> Optional[str]:
        encrypted_token = self._store.read(self._token_file_name)
        if not encrypted_token:
            return None
        return self._encryption_service.decrypt(encrypted_token)

    def save_bearer_token(self, token: str) -> None:
        encrypted_token = self._encryption_service.encrypt(token)
        self._store.write(self._token_file_name, encrypted_token)

    def prompt_for_bearer_token(self) -> str:
        """
        Opens a prompt for the user to input their
        YouTrack subdomain and bearer token.
        """

        bearer_token = display_bearer_token_prompt()

        if not bearer_token:
            raise UserCancelledError("User cancelled input. Exiting...")

        encrypted_bearer_token = self._encryption_service.encrypt(bearer_token)
        self._store.write(self._token_file_name, encrypted_bearer_token)

        return bearer_token
