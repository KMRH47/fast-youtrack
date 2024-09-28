from repositories.credentials_storage import read_credentials, read_passphrase, write_credentials, write_passphrase
from security.encryption import EncryptionService
from gui.credentials_gui import prompt_for_credentials
from models.credentials import Credentials
from errors.invalid_passphrase_error import InvalidPassphraseError
from errors.user_cancelled_error import UserCancelledError


class CredentialsService:
    """
    Service class to handle credentials.
    """

    def __init__(self, passphrase: str):
        """
        Initialize the credentials service.
        :param passphrase: The passphrase provided by the user
        """
        self.encryption_service = EncryptionService(passphrase)

    def _get_credentials(self) -> Credentials:
        encrypted_credentials = read_credentials()

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

        passphrase = read_passphrase()
        prompted_credentials = prompt_for_credentials(passphrase)

        write_credentials(Credentials(
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
