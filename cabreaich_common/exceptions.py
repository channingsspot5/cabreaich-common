# cabreaich_common/exceptions.py

class CabreaichError(Exception):
    """Base exception for the cabreaich project."""
    pass

class APIError(CabreaichError):
    """
    Exception raised for errors interacting with external APIs or internal services.

    Attributes:
        message (str): The primary error message.
        status_code (int | None): Optional HTTP status code associated with the error.
        fallback_message (str | None): Optional user-friendly fallback message to be spoken
                                        to the child if this error occurs.
    """
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        fallback_message: str | None = None # Added fallback_message
    ):
        """
        Initializes the APIError.

        Args:
            message: The primary error message.
            status_code: Optional HTTP status code.
            fallback_message: Optional user-friendly fallback message for TTS.
        """
        super().__init__(message)
        self.status_code = status_code
        self.fallback_message = fallback_message # Store the fallback message

    def __str__(self):
        # Keep the existing string representation
        if self.status_code:
            return f"[Status {self.status_code}] {super().__str__()}"
        return super().__str__()

class ValidationError(CabreaichError):
    """
    Exception raised for data validation errors (e.g., Pydantic validation).

    Attributes:
        message (str): The primary validation error message.
        details (dict | None): Optional dictionary containing detailed validation failures.
    """
    def __init__(self, message: str, details: dict | None = None):
        """
        Initializes the ValidationError.

        Args:
            message: The primary validation error message.
            details: Optional dictionary with detailed validation info.
        """
        super().__init__(message)
        self.details = details

# Add other specific, shared exceptions as needed
# Example:
# class ConfigurationError(CabreaichError):
#     """Exception raised for missing or invalid configuration."""
#     pass

# class DatabaseError(CabreaichError):
#     """Exception raised for database interaction errors."""
#     pass
