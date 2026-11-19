"""CP field parser for HJ 212-2017 protocol."""

from __future__ import annotations

from pyhj212.cp.models import CPField


class CPParser:
    """Parses CP (Command Parameter) field strings.

    CP fields use semicolons to separate key-value pairs,
    and commas to separate grouped data fields.

    Fields sharing the same factor code (prefix before '-') within a
    comma-delimited segment are merged into a single CPField whose
    *children* hold the individual attributes.

    Standalone fields without a factor code (e.g. DataTime, PNO) remain
    as flat CPField objects.
    """

    def parse(self, cp_string: str) -> list[CPField]:
        """Parse a CP field string into a list of CPField objects.

        Args:
            cp_string: The raw CP field string
                (e.g., ``'PNO=000000004;DataTime=20260902082000;'``
                ``'tn0112-Rtd=228.200,tn0112-Flag=N'``).

        Returns:
            List of CPField objects, with grouped factors as parents.

        Example:
            >>> parser = CPParser()
            >>> parser.parse("tn0112-Rtd=228.200,tn0112-Flag=N;DataTime=20261118134500")
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

            sub_parts = segment.split(",")

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

                if "-" in full_key:
                    factor_code, attr = full_key.split("-", 1)
                    has_factor = True
                    factor_groups.setdefault(factor_code, []).append((attr, value))
                else:
                    factor_groups.setdefault("__solo__", []).append((full_key, value))

            if has_factor and len(factor_groups) == 1:
                factor_code = next(iter(factor_groups))
                children = [
                    CPField(key=attr, value=val) for attr, val in factor_groups[factor_code]
                ]
                fields.append(CPField(key=factor_code, children=children, raw=segment))
            else:
                for sub_part in sub_parts:
                    sub_part = sub_part.strip()
                    if not sub_part:
                        continue
                    if "=" in sub_part:
                        key, value = sub_part.split("=", 1)
                        fields.append(CPField(key=key, value=value, raw=sub_part))
                    else:
                        fields.append(CPField(key=sub_part, raw=sub_part))

        return fields
