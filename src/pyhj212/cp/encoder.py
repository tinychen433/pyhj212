"""CP field encoder for HJ 212-2017 protocol."""

from __future__ import annotations

from pyhj212.cp.models import CPField


class CPEncoder:
    """Encodes CPField objects back into CP field strings."""

    def encode(self, fields: list[CPField]) -> str:
        """Encode a list of CPField objects into a CP string.

        Supports both flat fields (from ``parse()``) and grouped fields
        with children (from ``parse_grouped()``).

        Args:
            fields: List of CPField objects to encode.

        Returns:
            Semicolon-separated CP field string.
        """
        parts: list[str] = []
        for field_item in fields:
            if field_item.children:
                # Grouped field: tn0112 with Rtd, Flag children
                sub_parts = [
                    f"{field_item.key}-{child.key}={child.value}" for child in field_item.children
                ]
                parts.append(",".join(sub_parts))
            elif field_item.value:
                parts.append(f"{field_item.key}={field_item.value}")
            else:
                parts.append(field_item.key)
        return ";".join(parts)
