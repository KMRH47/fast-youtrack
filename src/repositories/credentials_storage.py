import os
import logging
import yaml
from models.credentials import Credentials
from pydantic import ValidationError
from typing import Optional


def get_data_directory_path() -> str:
    """
    Returns the path to the 'data' directory.
    """
    return os.path.join(os.path.dirname(__file__), '../../data')


def get_credentials_file_path() -> str:
    """
    Returns the path to the 'user-config.yaml' file in the 'data' directory.
    """
    return os.path.join(get_data_directory_path(), 'user-config.yaml')


def write_credentials(credentials: Credentials) -> None:
    """
    Writes the credentials to 'user-config.yaml' file in the 'data' directory.
    """
    credentials_dir = get_data_directory_path()

    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)

    credentials_file = get_credentials_file_path()

    with open(credentials_file, 'w') as file:
        yaml.dump(credentials.model_dump(), file)

    logging.info("Credentials saved to file")


def read_credentials() -> Optional[Credentials]:
    """
    Loads credentials from the 'user-config.yaml' file located in the 'data' directory.
    Returns a validated Credentials object if successful, or None if validation fails.
    """
    credentials_file = get_credentials_file_path()

    if not os.path.exists(credentials_file):
        logging.warning(f"Credentials file not found: {credentials_file}")
        return None

    try:
        with open(credentials_file, 'r') as file:
            credentials_data = yaml.safe_load(file)

        if isinstance(credentials_data, dict):
            credentials = Credentials(**credentials_data)
            logging.info(
                f"Credentials loaded from {credentials_file}")
            return credentials
        else:
            logging.error(
                f"Expected a dictionary for credentials but got: {type(credentials_data)}")
            return None

    except FileNotFoundError:
        logging.error(f"Credentials file not found: {credentials_file}")
        return None
    except ValidationError as e:
        logging.error(f"Validation error: {e}")
        return None
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        return None


def write_passphrase(passphrase: str, filename: str = ".key"):
    """
    Writes the passphrase to a file in the 'data' directory.
    """
    passphrase_dir = get_data_directory_path()

    if not os.path.exists(passphrase_dir):
        os.makedirs(passphrase_dir)

    passphrase_file = os.path.join(passphrase_dir, filename)
    try:
        with open(passphrase_file, "w") as f:
            f.write(passphrase)
    except Exception as e:
        logging.error(
            f"Failed to write passphrase to {passphrase_file}: {e}")


def read_passphrase() -> Optional[str]:
    """
    Reads the passphrase from a file in the 'data' directory.
    """
    passphrase_file = os.path.join(get_data_directory_path(), ".key")
    try:
        with open(passphrase_file, "r") as f:
            passphrase = f.read()
        return passphrase
    except Exception as e:
        logging.error(f"Failed to read passphrase from {passphrase_file}: {e}")
        return None
