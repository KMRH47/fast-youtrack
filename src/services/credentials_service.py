import logging
from typing import Tuple
from repositories.credentials_storage import read_credentials, read_passphrase, write_credentials, write_passphrase
from security.encryption import EncryptionService
from gui.credentials_gui import prompt_for_credentials
from models.credentials import Credentials
from errors.invalid_passphrase_error import InvalidPassphraseError


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

    def save_credentials(self, subdomain: str, bearer_token: str, author_id: str, author_name: str):
        encrypted_bearer_token = self.encryption_service.encrypt(bearer_token)

        write_credentials(Credentials(
            subdomain=subdomain,
            bearer_token=encrypted_bearer_token,
            author_id=author_id,
            author_name=author_name
        ))

    def prompt_token_and_subdomain(self, passphrase: str) -> Tuple[str, str]:
        subdomain, bearer_token = prompt_for_credentials(passphrase)

        if not subdomain or not bearer_token:
            logging.error("User cancelled credentials input. Exiting...")
            exit(1)

        return (subdomain, bearer_token)


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