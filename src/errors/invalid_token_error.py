from errors.user_error import UserError


class InvalidTokenError(UserError):
    def __init__(self):
        super().__init__("Invalid token. Please delete the associated '.token' file and try again.")
