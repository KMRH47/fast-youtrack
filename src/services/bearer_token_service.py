from security.encryption import EncryptionService
from errors.user_cancelled_error import UserCancelledInputError
from repositories.file_manager import FileManager
from ui.token_ui import display_bearer_token_prompt
import logging


logger = logging.getLogger(__name__)


class BearerTokenService:
    def __init__(self, base_dir: str, passphrase: str):
        """
        Initialize the TokenService.

        :param passphrase: The passphrase provided by the user. Used to derive the encryption key.
        :param subdomain: The YouTrack subdomain provided by the user.
        """

        self.file_manager = FileManager(base_dir, ".token")
        self.encryption_service = EncryptionService(passphrase)

    def get_bearer_token(self) -> str | None:
        encrypted_bearer_token = self.file_manager.read_data()

        if not encrypted_bearer_token:
            return None

        return self.encryption_service.decrypt(encrypted_bearer_token)

    def prompt_for_bearer_token(self) -> str:
        """
        Opens a prompt for the user to input their YouTrack subdomain and bearer token.
        """

        bearer_token = display_bearer_token_prompt()

        if not bearer_token:
            raise UserCancelledInputError("User cancelled input. Exiting...")

        encrypted_bearer_token = self.encryption_service.encrypt(bearer_token)
        self.file_manager.write_data(encrypted_bearer_token)

        return bearer_token
