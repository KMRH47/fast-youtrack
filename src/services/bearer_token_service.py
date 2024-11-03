import logging

from security.encryption import EncryptionService
from errors.user_cancelled_error import UserCancelledError
from repositories.file_manager import FileManager
from ui.token_ui import display_bearer_token_prompt


logger = logging.getLogger(__name__)

class BearerTokenService:
    def __init__(self, file_manager: FileManager, encryption_service: EncryptionService, token_file_name: str):
        """
        Initialize the TokenService.

        :param file_manager: The file manager for reading and writing token data.
        :param encryption_service: The encryption service for encrypting and decrypting tokens.
        :param token_file_name: The name of the file where the token is stored.
        """
        self.__file_manager = file_manager
        self.__encryption_service = encryption_service
        self.file_name = token_file_name

    def get_bearer_token(self) -> str | None:
        encrypted_bearer_token = self.__file_manager.read_data(self.file_name)

        if not encrypted_bearer_token:
            return None

        return self.__encryption_service.decrypt(encrypted_bearer_token)

    def prompt_for_bearer_token(self) -> str:
        """
        Opens a prompt for the user to input their
        YouTrack subdomain and bearer token.
        """

        bearer_token = display_bearer_token_prompt()

        if not bearer_token:
            raise UserCancelledError("User cancelled input. Exiting...")

        encrypted_bearer_token = self.__encryption_service.encrypt(
            bearer_token)
        self.__file_manager.write_data(encrypted_bearer_token, self.file_name)

        return bearer_token
