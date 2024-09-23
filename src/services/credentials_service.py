import logging
from typing import Tuple
from repositories.credentials_storage import get_data_directory_path, load_credentials, save_credentials
from security.encryption import EncryptionService
from gui.credentials_gui import prompt_for_credentials
from models.credentials import Credentials


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
        """Get saved credentials."""

        encrypted_credentials = load_credentials()

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
        """Save credentials."""
        encrypted_bearer_token = self.encryption_service.encrypt(bearer_token)

        save_credentials(
            subdomain=subdomain,
            bearer_token=encrypted_bearer_token,
            author_id=author_id,
            author_name=author_name
        )

    def prompt_token_and_subdomain(self, passphrase: str) -> Tuple[str, str]:
        """Prompt user for token and subdomain."""
        subdomain, bearer_token = prompt_for_credentials(passphrase)

        if not subdomain or not bearer_token:
            logging.error("User cancelled credentials input. Exiting...")
            exit(1)

        return (subdomain, bearer_token)
