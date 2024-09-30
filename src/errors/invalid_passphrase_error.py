from errors.user_error import UserError


class InvalidPassphraseError(UserError):
    def __init__(self):
        super().__init__("Invalid passphrase. Please delete the associated '.key' file and try again.")
