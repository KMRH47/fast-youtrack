class InvalidPassphraseError(Exception):
    """Exception raised for invalid passphrases."""
    def __init__(self, message="The provided passphrase is invalid."):
        self.message = message
        super().__init__(self.message)
