from gui.error_gui import display_error_dialog


class UserError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def display(self):
        display_error_dialog(self.message)
