"""Custom exceptions for the HJ 212-2017 protocol library."""

from __future__ import annotations


class PyHJ212Error(Exception):
    """Base exception for all PyHJ212 errors."""


class ParseError(PyHJ212Error):
    """Raised when message parsing fails."""

    def __init__(self, message: str, position: int = 0) -> None:
        super().__init__(message)
        self.position = position


class EncodeError(PyHJ212Error):
    """Raised when message encoding fails."""


class ValidationError(PyHJ212Error):
    """Raised when protocol validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


class ChecksumError(ValidationError):
    """Raised when CRC verification fails."""


class CPError(ParseError):
    """Raised when CP field parsing fails."""
