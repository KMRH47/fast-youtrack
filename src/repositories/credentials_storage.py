from models.credentials import Credentials
from pydantic import ValidationError
from typing import Optional
import os
import logging
import yaml

logger = logging.getLogger(__name__)


class CredentialsStorage:
    def __init__(self, subdomain: str):
        self.credentials_path = os.path.join(
            self.user_settings_path, subdomain, 'credentials.yaml')
        self.user_settings_path = os.path.join(
            os.path.dirname(__file__), '../../user-settings')

    def write_credentials(self, credentials: Credentials) -> None:
        credentials_file = self.credentials_path()
        os.makedirs(os.path.dirname(credentials_file), exist_ok=True)

        with open(credentials_file, 'w') as file:
            yaml.dump(credentials.model_dump(), file)

        logger.info(f'Credentials written to {credentials_file}')

    def read_credentials(self) -> Optional[Credentials]:
        if not os.path.exists(self.credentials_path):
            logger.warning(
                f"Credentials file not found: {self.credentials_path}")
            return None

        try:
            with open(self.credentials_path, 'r') as file:
                credentials_data = yaml.safe_load(file)

            if isinstance(credentials_data, dict):
                credentials = Credentials(**credentials_data)
                logger.info(f"Credentials loaded from {self.credentials_path}")
                return credentials
            else:
                logger.error(
                    f"Expected a dictionary for credentials but got: {type(credentials_data)}")
                return None

        except (FileNotFoundError, ValidationError, yaml.YAMLError) as e:
            logger.error(f"Error reading credentials: {e}")
            return None

    def write_passphrase(self, passphrase: str) -> None:
        passphrase_file = os.path.join(self.user_settings_path, '.key')

        os.makedirs(self.user_settings_path, exist_ok=True)

        try:
            with open(passphrase_file, "w") as f:
                f.write(passphrase)
        except Exception as e:
            logger.error(
                f"Failed to write passphrase to {passphrase_file}: {e}")

    def read_passphrase(self) -> Optional[str]:
        passphrase_file = os.path.join(self.user_settings_path, ".key")

        try:
            with open(passphrase_file, "r") as f:
                return f.read()
        except Exception as e:
            logger.error(
                f"Failed to read passphrase from {passphrase_file}: {e}")
            return None
