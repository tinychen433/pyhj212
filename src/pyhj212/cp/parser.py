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

    def parse_grouped(self, cp_string: str) -> list[CPField]:
        """Parse CP data with monitoring factors grouped by factor code.

        Fields sharing the same factor code (prefix before '-') within a
        semicolon-delimited segment are merged into a single CPField whose
        *children* hold the individual attributes.

        Standalone fields without a factor code (e.g. DataTime, PNO) remain
        as flat CPField objects.

        Args:
            cp_string: The raw CP field string.

        Returns:
            List of CPField objects, with grouped factors as parents.

        Example:
            >>> parser = CPParser()
            >>> parser.parse_grouped("tn0112-Rtd=228.200,tn0112-Flag=N;DataTime=20261118134500")
            [
                CPField(key="tn0112", children=[
                    CPField(key="Rtd", value="228.200"),
                    CPField(key="Flag", value="N"),
                ]),
                CPField(key="DataTime", value="20261118134500"),
            ]
        """
        if not cp_string:
            return []

        fields: list[CPField] = []
        segments = cp_string.split(";")

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            # Split by comma to get sub-fields within this segment
            sub_parts = segment.split(",")

            # Check if all sub-parts share the same factor code (have '-' prefix)
            factor_groups: dict[str, list[tuple[str, str]]] = {}
            has_factor = False

            for sub_part in sub_parts:
                sub_part = sub_part.strip()
                if not sub_part:
                    continue

                if "=" in sub_part:
                    full_key, value = sub_part.split("=", 1)
                else:
                    full_key = sub_part
                    value = ""

                # Extract factor code: part before '-' if present
                if "-" in full_key:
                    factor_code, attr = full_key.split("-", 1)
                    has_factor = True
                    factor_groups.setdefault(factor_code, []).append((attr, value))
                else:
                    # Standalone field without factor code
                    factor_groups.setdefault("__solo__", []).append((full_key, value))

            if has_factor and len(factor_groups) == 1:
                # All sub-parts share the same factor — group them
                factor_code = next(iter(factor_groups))
                children = [
                    CPField(key=attr, value=val) for attr, val in factor_groups[factor_code]
                ]
                fields.append(CPField(key=factor_code, children=children, raw=segment))
            else:
                # Mixed or no factor — fall back to flat parsing
                flat_fields = self.parse(segment)
                fields.extend(flat_fields)

        return fields
