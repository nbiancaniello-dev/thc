class AppException(Exception):
    """Base exception for application domain errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ResourceNotFoundError(AppException):
    """Raised when a requested resource does not exist."""
    pass


class DuplicateResourceError(AppException):
    """Raised when an entity with a unique field already exists."""
    pass


class InvalidCredentialsError(AppException):
    """Raised when user authentication fails."""
    pass


class ForbiddenError(AppException):
    """Raised when an authenticated user does not have permission for an action."""
    pass
