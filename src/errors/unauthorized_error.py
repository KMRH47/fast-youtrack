from errors.user_error import UserError


class UnauthorizedError(UserError):
    def __init__(self):
        super().__init__("Unauthorized. Please check subdomain and token.")
