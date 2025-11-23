"""Custom exceptions for Zeta Reason."""

from typing import Any, Optional


class ProviderError(Exception):
    """
    Exception raised when a model provider (OpenAI, etc.) encounters an error.

    This exception includes structured error information that can be
    converted to an ErrorResponse for the API.
    """

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize ProviderError.

        Args:
            message: Human-readable error message
            provider: Name of the provider (e.g., 'openai')
            status_code: HTTP status code from provider API (if applicable)
            error_code: Error code from provider API (if applicable)
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for ErrorResponse."""
        details = {
            "provider": self.provider,
            **self.details,
        }
        if self.status_code is not None:
            details["status_code"] = self.status_code
        if self.error_code is not None:
            details["error_code"] = self.error_code
        return {
            "error": self.message,
            "details": details,
        }
