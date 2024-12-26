import logging
import os
import base64
import binascii

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from errors.user_error import UserError

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Service class to handle encryption and decryption of tokens.
    """

    def __init__(self, passphrase: str):
        """
        Initialize the encryption service.

        :param passphrase: The passphrase provided by the user.
        Used to derive the encryption key.
        """
        self.key = self.derive_key(passphrase)

    @staticmethod
    def derive_key(passphrase: str) -> bytes:
        """
        Derives a key from the passphrase using PBKDF2 with SHA-256.

        :param passphrase: The passphrase provided by the user
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"",
            iterations=100000,
            backend=default_backend(),
        )
        return kdf.derive(passphrase.encode())

    def encrypt(self, value: str) -> str:
        """
        Encrypts a value using AES-GCM.

        :param value: The value to encrypt
        """
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        encrypted_value = aesgcm.encrypt(nonce, value.encode(), None)
        return base64.b64encode(nonce + encrypted_value).decode()

    def decrypt(self, encrypted_value: str) -> str:
        """
        Decrypts a value using AES-GCM.

        :param encrypted_value: The encrypted value as a base64-encoded string
        """
        try:
            aesgcm = AESGCM(self.key)
            decoded_data = base64.b64decode(encrypted_value)
            nonce = decoded_data[:12]
            encrypted_value = decoded_data[12:]
            return aesgcm.decrypt(nonce, encrypted_value, None).decode()
        except InvalidTag as e:
            raise UserError(
                "Invalid passphrase. Please delete the associated \
                  '.key' file and try again."
            ) from e
        except binascii.Error as e:
            raise UserError(
                "Invalid token. Please delete the associated \
                  '.token' file and try again."
            ) from e
