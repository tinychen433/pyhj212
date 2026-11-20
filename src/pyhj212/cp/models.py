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

    def to_dict(self) -> dict[str, object]:
        """Convert to a simplified JSON-serializable dictionary.

        Returns a dict keyed by the field name, with children nested as
        a dict of attribute name to value.

        Returns:
            Dict like ``{"tn0103": {"Rtd": "228.200", "Flag": "N"}}`` for
            grouped fields, or ``{"DataTime": "20261118134500"}`` for
            standalone fields.
        """
        if self.children:
            return {self.key: {c.key: c.value for c in self.children}}
        return {self.key: self.value} if self.value else {self.key: ""}

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> CPField:
        """Create a CPField from a dict produced by ``to_dict()``.

        Args:
            d: A single-key dict like ``{"tn0112": {"Rtd": "228.200"}}``
               (grouped) or ``{"DataTime": "20261118134500"}`` (flat).

        Returns:
            A CPField instance.

        Example:
            >>> CPField.from_dict({"tn0112": {"Rtd": "228.200", "Flag": "N"}})
            CPField(key='tn0112', value='', children=[...])
            >>> CPField.from_dict({"DataTime": "20261118134500"})
            CPField(key='DataTime', value='20261118134500')
        """
        key, val = next(iter(d.items()))
        if isinstance(val, dict):
            children = [cls(key=k, value=str(v)) for k, v in val.items()]
            return cls(key=key, children=children)
        return cls(key=key, value=str(val) if val is not None else "")
