"""
Custom exception classes for the IBS Wellness Companion API.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class IBSException(HTTPException):
    """Base exception class for IBS Wellness Companion."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationError(IBSException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(IBSException):
    """Raised when user is not authorized to perform an action."""

    def __init__(self, detail: str = "Not authorized to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundError(IBSException):
    """Raised when a resource is not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ValidationError(IBSException):
    """Raised when input validation fails."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ConflictError(IBSException):
    """Raised when there's a conflict with existing data."""

    def __init__(self, detail: str = "Conflict with existing data"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class RateLimitError(IBSException):
    """Raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )


class MLModelError(IBSException):
    """Raised when ML model operations fail."""

    def __init__(self, detail: str = "ML model error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class DatabaseError(IBSException):
    """Raised when database operations fail."""

    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class ExternalServiceError(IBSException):
    """Raised when external service calls fail."""

    def __init__(self, detail: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )
