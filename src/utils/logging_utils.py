import traceback


def format_error_message(error: Exception) -> str:
    """Format an exception into a user-friendly error message with stack trace."""
    error_type = type(error).__name__
    error_details = traceback.format_exc()
    return f"An unexpected error occurred\n\nError Type: {error_type}\nDetails: {error_details}"
