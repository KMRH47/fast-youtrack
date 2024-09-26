class InvalidTokenError(Exception):
    """Exception raised for invalid tokens."""
    def __init__(self, message="The provided token is invalid."):
        self.message = message
        super().__init__(self.message)
