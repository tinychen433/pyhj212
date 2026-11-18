"""CP field parser for HJ 212-2017 protocol."""

from __future__ import annotations

from pyhj212.cp.models import CPField


class CPParser:
    """Parses CP (Command Parameter) field strings.

    CP fields use semicolons to separate key-value pairs,
    and commas to separate grouped data fields.
    """

    def parse(self, cp_string: str) -> list[CPField]:
        """Parse a CP field string into a list of CPField objects.

        Args:
            cp_string: The raw CP field string (e.g., 'w01001-Rtd=12.5;w01002-Rtd=34.0').

        Returns:
            List of parsed CPField objects.
        """
        if not cp_string:
            return []

        fields: list[CPField] = []
        parts = cp_string.split(";")

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if "=" in part:
                key, value = part.split("=", 1)
                fields.append(CPField(key=key, value=value, raw=part))
            else:
                fields.append(CPField(key=part, raw=part))

        return fields
