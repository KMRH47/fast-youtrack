import logging
from security.encryption import EncryptionService
from errors.user_cancelled_error import UserCancelledInputError
from repositories.bearer_token_repository import TokenRepository
from gui.token_gui import display_bearer_token_prompt


logger = logging.getLogger(__name__)


class BearerTokenService:
    def __init__(self, base_path: str, passphrase: str):
        """
        Initialize the TokenService.

        :param passphrase: The passphrase provided by the user. Used to derive the encryption key.
        :param subdomain: The YouTrack subdomain provided by the user.
        """

        self.token_repository = TokenRepository(base_path)
        self.encryption_service = EncryptionService(passphrase)

    def get_bearer_token(self) -> str:
        encrypted_bearer_token = self.token_repository.read_token()

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
        self.token_repository.write_token(encrypted_bearer_token)

        return bearer_token
