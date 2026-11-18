"""Validation result model for protocol validation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of validating an HJ 212-2017 message.

    Attributes:
        is_valid: Whether the message passed all validation checks.
        errors: List of validation error messages.
        warnings: List of non-critical warnings.
    """

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add a validation error."""
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(message)
