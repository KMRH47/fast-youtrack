import logging
from security.encryption import EncryptionService
from gui.credentials_gui import prompt_for_credentials
from models.credentials import Credentials
from errors.invalid_passphrase_error import InvalidPassphraseError
from errors.user_cancelled_error import UserCancelledError
from repositories.credentials_storage import CredentialsStorage


logger = logging.getLogger(__name__)


class CredentialsService:
    """
    Service class to handle credentials.
    """

    def __init__(self, credentials_storage: CredentialsStorage, passphrase: str):
        """
        Initialize the credentials service.
        :param passphrase: The passphrase provided by the user
        """
        self.encryption_service = EncryptionService(passphrase)
        self.credentials_storage = credentials_storage

    def _get_credentials(self) -> Credentials:
        encrypted_credentials = self.credentials_storage.read_credentials()

        if not encrypted_credentials:
            return None

        bearer_token = self.encryption_service.decrypt(
            encrypted_credentials.bearer_token)

        return Credentials(
            subdomain=encrypted_credentials.subdomain,
            bearer_token=bearer_token,
        )

    def handle_credentials(self) -> Credentials:

        stored_credentials = self._get_credentials()
        if stored_credentials:
            return stored_credentials

        passphrase = self.credentials_storage.read_passphrase()
        prompted_credentials = prompt_for_credentials(passphrase)

        self.credentials_storage.write_credentials(Credentials(
            subdomain=prompted_credentials.subdomain,
            bearer_token=self.encryption_service.encrypt(
                prompted_credentials.bearer_token)
        ))

        return prompted_credentials

    def prompt_for_credentials(self) -> Credentials:
        """
        Opens a prompt for the user to input their YouTrack subdomain and bearer token.
        """

        credentials = self._get_credentials()

        if not credentials:
            raise UserCancelledError(
                "User cancelled credentials input. Exiting...")

        return credentials

    def handle_passphrase(self, passphrase: str | None) -> None:
        if not passphrase:
            passphrase = CredentialsStorage.read_passphrase()
            if not passphrase:
                raise InvalidPassphraseError()
            return passphrase

        logger.info(f"Passphrase provided as argument.: {passphrase}")

        self.credentials_storage.write_passphrase(passphrase)
        return passphrase
