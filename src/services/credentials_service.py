from typing import Tuple
from repositories.credentials_storage import read_credentials, read_passphrase, write_credentials, write_passphrase
from security.encryption import EncryptionService
from gui.credentials_gui import prompt_for_credentials
from models.credentials import Credentials
from errors.invalid_passphrase_error import InvalidPassphraseError
from models.work_item_response import WorkItemResponse
from services.youtrack_service import YouTrackService
from errors.user_cancelled_error import UserCancelledError


class CredentialsService:
    """
    Service class to handle loading and saving credentials.
    """

    def __init__(self, passphrase: str):
        """
        Initialize the credentials service.
        :param passphrase: The passphrase provided by the user
        """
        self.encryption_service = EncryptionService(passphrase)

    def get_credentials(self) -> Credentials:
        encrypted_credentials = read_credentials()

        if not encrypted_credentials:
            return None

        bearer_token = self.encryption_service.decrypt(
            encrypted_credentials.bearer_token)

        return Credentials(
            subdomain=encrypted_credentials.subdomain,
            bearer_token=bearer_token,
            author_id=encrypted_credentials.author_id,
            author_name=encrypted_credentials.author_name
        )

    def prompt_token_and_subdomain(self, passphrase: str) -> Tuple[str, str]:
        subdomain, bearer_token = prompt_for_credentials(passphrase)

        if not subdomain or not bearer_token:
            raise UserCancelledError(
                "User cancelled credentials input. Exiting...")

        return (subdomain, bearer_token)

    def load_or_save_credentials(self, passphrase):
        credentials = self.get_credentials()
        if credentials:
            return credentials

        subdomain, bearer_token = self.prompt_token_and_subdomain(
            passphrase)
        youtrack_service = YouTrackService(subdomain, bearer_token)
        user_info: WorkItemResponse = youtrack_service.get_user_info()

        write_credentials(Credentials(
            subdomain=subdomain,
            bearer_token=self.encryption_service.encrypt(bearer_token),
            author_id=user_info.id,
            author_name=user_info.name
        ))
        return self.get_credentials()


def handle_passphrase(passphrase: str | None) -> str:
    """
    Handles passphrase verification or storage.

    :param passphrase: The passphrase to handle
    :raise InvalidPassphraseError: If the passphrase is invalid.
    """
    if not passphrase:
        passphrase = read_passphrase()
        if not passphrase:
            raise InvalidPassphraseError()
        return passphrase

    write_passphrase(passphrase)
    return passphrase
