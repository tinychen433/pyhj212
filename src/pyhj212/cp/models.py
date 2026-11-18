"""CP field data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CPField:
    """Represents a parsed CP (Command Parameter) field.

    CP fields contain key-value pairs and nested data groups
    used for transmitting monitoring data and control commands.

    Attributes:
        key: The CP field identifier (e.g., 'w01001-Rtd').
        value: The field value string.
        children: Nested child fields for grouped data.
        raw: Original raw field string for preservation.
    """

    key: str
    value: str = ""
    children: list[CPField] = field(default_factory=list, repr=False)
    raw: str = field(default="", repr=False, compare=False)

    def get_child(self, key: str) -> CPField | None:
        """Find a child field by key.

        Args:
            key: The child field key to search for.

        Returns:
            The matching CPField, or None if not found.
        """
        for child in self.children:
            if child.key == key:
                return child
        return None
