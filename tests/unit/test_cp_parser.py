"""Tests for CP field parsing."""

from __future__ import annotations

import json

from pyhj212.cp.models import CPField
from pyhj212.cp.parser import CPParser

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# CP data from real CN=2051 message (44 fields)
REALTIME_CP_DATA = (
    "PNO=000000004;DataTime=20260902082000;RtdInterval=300;"
    "RestartTime=20260902064138;"
    "a34004-Avg=3.000;a34002-Avg=4.000;ys0017-Avg=5.000;ys0019-Avg=5.000;"
    "ys0018-Avg=-99.000;ys0020-Avg=-99.000;ys0021-Avg=5.000;a05024-Avg=-99.00;"
    "a21026-Avg=-99.00;a21004-Avg=-99.0;a21005-Avg=-99.000;a99054-Avg=-99.000;"
    "ys0025-Avg=0.000;ys0026-Avg=0.000;ys0023-Avg=0.000;ys0024-Avg=0.000;"
    "ys0027-Avg=0.000;ys0028-Avg=0.000;ys0029-Avg=0.000;ys0030-Avg=0.000;"
    "ys0031-Avg=0.000;ys0032-Avg=0.000;"
    "a01012-Rtd=36.0;a01014-Rtd=30.4;a01001-Rtd=24.4;a01002-Rtd=59.6;"
    "ys0111-Rtd=24.4;ys0007-Rtd=116.489983;ys0008-Rtd=39.902966;"
    "ys0034-Rtd=-99.000;a01006-Rtd=-99.000;a01007-Avg=-99.0;a01008-Avg=-99;"
    "ys0009-Rtd=31;ys0013-Rtd=0;ys0010-Rtd=0;ys0011-Rtd=75;ys0012-Rtd=50;"
    "ys0002-Rtd=162.005;ys0014-Rtd=89860473102590002828"
)

# Simple CP data with common pollutant factors
SIMPLE_CP_DATA = "w01001-Rtd=12.5;w01002-Rtd=34.0;w01003-Rtd=5.67"

# ---------------------------------------------------------------------------
# Valid CP parsing
# ---------------------------------------------------------------------------


class TestParseValidCP:
    """Tests for successful CP field parsing."""

    def setup_method(self) -> None:
        self.parser = CPParser()

    def test_realtime_cp_data(self) -> None:
        """Parse real-world CP data with 44 fields."""
        fields = self.parser.parse(REALTIME_CP_DATA)

        assert len(fields) == 44

        # Control fields
        pno = fields[0]
        assert pno.key == "PNO"
        assert pno.value == "000000004"

        datatime = fields[1]
        assert datatime.key == "DataTime"
        assert datatime.value == "20260902082000"

        # Pollutant factors (Avg values) — index 4 is first Avg after RestartTime
        avg_field = fields[4]
        assert avg_field.key == "a34004-Avg"
        assert avg_field.value == "3.000"

        # Negative values (invalid data marker) — ys0018 is the 7th data field
        neg_field = fields[8]
        assert neg_field.key == "ys0018-Avg"
        assert neg_field.value == "-99.000"

    def test_simple_cp_data(self) -> None:
        """Parse simple CP data with Rtd values."""
        fields = self.parser.parse(SIMPLE_CP_DATA)

        assert len(fields) == 3
        assert fields[0].key == "w01001-Rtd"
        assert fields[0].value == "12.5"
        assert fields[1].key == "w01002-Rtd"
        assert fields[1].value == "34.0"

    def test_single_field(self) -> None:
        """Parse a single key=value pair."""
        fields = self.parser.parse("w01001-Rtd=12.5")
        assert len(fields) == 1
        assert fields[0].key == "w01001-Rtd"
        assert fields[0].value == "12.5"

    def test_empty_string(self) -> None:
        """Empty string returns empty list."""
        assert self.parser.parse("") == []

    def test_field_without_value(self) -> None:
        """Field without = gets empty value."""
        fields = self.parser.parse("FlagMarker")
        assert len(fields) == 1
        assert fields[0].key == "FlagMarker"
        assert fields[0].value == ""

    def test_negative_values(self) -> None:
        """Negative numeric values are preserved."""
        fields = self.parser.parse("a01001-Avg=-99.000")
        assert fields[0].value == "-99.000"

    def test_zero_values(self) -> None:
        """Zero values parse correctly."""
        fields = self.parser.parse("ys0010-Rtd=0")
        assert fields[0].value == "0"

    def test_very_long_value(self) -> None:
        """Very long values (e.g. ICCID 20 digits) parse correctly."""
        fields = self.parser.parse("ys0014-Rtd=89860473102590002828")
        assert fields[0].value == "89860473102590002828"
        assert len(fields[0].value) == 20

    def test_high_precision_value(self) -> None:
        """High precision decimal values are preserved exactly."""
        fields = self.parser.parse("ys0007-Rtd=116.489983")
        assert fields[0].value == "116.489983"

    def test_varied_decimal_places(self) -> None:
        """Values with different decimal precision are preserved."""
        fields = self.parser.parse("a01007-Avg=-99.0;a01008-Avg=-99;a05024-Avg=-99.00")
        assert fields[0].value == "-99.0"
        assert fields[1].value == "-99"
        assert fields[2].value == "-99.00"

    def test_raw_field_preservation(self) -> None:
        """Raw field string is preserved."""
        fields = self.parser.parse("a34004-Avg=3.000")
        assert fields[0].raw == "a34004-Avg=3.000"

    def test_trailing_semicolon(self) -> None:
        """Trailing semicolon is handled gracefully."""
        fields = self.parser.parse("w01001-Rtd=12.5;")
        assert len(fields) == 1
        assert fields[0].key == "w01001-Rtd"
        assert fields[0].value == "12.5"

    def test_multiple_trailing_semicolons(self) -> None:
        """Multiple trailing semicolons don't create extra fields."""
        fields = self.parser.parse("w01001-Rtd=12.5;;;")
        assert len(fields) == 1

    def test_control_fields(self) -> None:
        """Control fields (PNO, DataTime, RtdInterval) parse correctly."""
        fields = self.parser.parse("PNO=000000004;DataTime=20260902082000;RtdInterval=300")
        assert len(fields) == 3

        assert fields[0].key == "PNO"
        assert fields[0].value == "000000004"

        assert fields[1].key == "DataTime"
        assert fields[1].value == "20260902082000"

        assert fields[2].key == "RtdInterval"
        assert fields[2].value == "300"

    # -----------------------------------------------------------------------
    # CPField model tests
    # -----------------------------------------------------------------------

    def test_get_child_found(self) -> None:
        """CPField.get_child returns matching child."""
        parent = CPField(
            key="group",
            children=[
                CPField(key="a", value="1"),
                CPField(key="b", value="2"),
            ],
        )
        child = parent.get_child("b")
        assert child is not None
        assert child.value == "2"

    def test_get_child_not_found(self) -> None:
        """CPField.get_child returns None for missing key."""
        parent = CPField(key="group", children=[CPField(key="a", value="1")])
        assert parent.get_child("z") is None

    def test_get_child_empty_children(self) -> None:
        """CPField.get_child with no children returns None."""
        parent = CPField(key="solo", value="test")
        assert parent.get_child("anything") is None


# ---------------------------------------------------------------------------
# Grouped CP parsing (parse_grouped)
# ---------------------------------------------------------------------------


class TestParseGroupedCP:
    """Tests for CPParser.parse_grouped() with factor-code grouping."""

    def setup_method(self) -> None:
        self.parser = CPParser()

    def test_single_factor_grouped(self) -> None:
        """Comma-separated fields with same factor code are grouped."""
        cp = "tn0112-Rtd=228.200,tn0112-Flag=N"
        fields = self.parser.parse_grouped(cp)

        assert len(fields) == 1
        assert fields[0].key == "tn0112"
        assert fields[0].value == ""
        assert len(fields[0].children) == 2
        assert fields[0].children[0].key == "Rtd"
        assert fields[0].children[0].value == "228.200"
        assert fields[0].children[1].key == "Flag"
        assert fields[0].children[1].value == "N"

    def test_mixed_standalone_and_grouped(self) -> None:
        """Standalone fields and grouped factors coexist."""
        cp = "DataTime=20261118134500;tn0112-Rtd=228.200,tn0112-Flag=N;tn0110-Rtd=229.100,tn0110-Flag=N"
        fields = self.parser.parse_grouped(cp)

        assert len(fields) == 3
        # DataTime is standalone
        assert fields[0].key == "DataTime"
        assert fields[0].value == "20261118134500"
        assert fields[0].children == []
        # tn0112 is grouped
        assert fields[1].key == "tn0112"
        assert fields[1].children[0].key == "Rtd"
        assert fields[1].children[1].key == "Flag"
        # tn0110 is grouped
        assert fields[2].key == "tn0110"
        assert fields[2].children[0].value == "229.100"

    def test_real_device_message(self) -> None:
        """Parse real-world device data with multiple factors."""
        cp = (
            "DataTime=20261118134500;"
            "tn0112-Rtd=228.200,tn0112-Flag=N;"
            "tn0110-Rtd=229.100,tn0110-Flag=N;"
            "tn0109-Rtd=1.000,tn0109-Flag=N;"
            "tn0105-Rtd=0.000,tn0105-Flag=N;"
            "tn0107-Rtd=0.0,tn0107-Flag=N;"
            "tn0111-Rtd=230.000,tn0111-Flag=N;"
            "tn0108-Rtd=0.0,tn0108-Flag=N;"
            "tn0101-Rtd=0.000,tn0101-Flag=N;"
            "tn0102-Rtd=0.000,tn0102-Flag=N;"
            "tn0106-Rtd=0.000,tn0106-Flag=N"
        )
        fields = self.parser.parse_grouped(cp)

        # 1 DataTime + 10 factor groups = 11 fields
        assert len(fields) == 11

        # Check DataTime
        assert fields[0].key == "DataTime"
        assert fields[0].value == "20261118134500"

        # Check first factor
        tn0112 = fields[1]
        assert tn0112.key == "tn0112"
        assert tn0112.get_child("Rtd") is not None
        assert tn0112.get_child("Rtd").value == "228.200"
        assert tn0112.get_child("Flag").value == "N"

        # Check a zero-value factor
        tn0105 = fields[4]
        assert tn0105.key == "tn0105"
        assert tn0105.get_child("Rtd").value == "0.000"

    def test_standalone_fields_unchanged(self) -> None:
        """Fields without factor code remain flat."""
        cp = "PNO=000000004;DataTime=20260902082000;RtdInterval=300"
        fields = self.parser.parse_grouped(cp)

        assert len(fields) == 3
        for f in fields:
            assert f.children == []
            assert "-" not in f.key

        assert fields[0].key == "PNO"
        assert fields[1].key == "DataTime"
        assert fields[2].key == "RtdInterval"

    def test_empty_string(self) -> None:
        """Empty string returns empty list."""
        assert self.parser.parse_grouped("") == []

    def test_single_factor_no_comma(self) -> None:
        """Single factor without comma still groups."""
        cp = "tn0112-Rtd=228.200"
        fields = self.parser.parse_grouped(cp)

        assert len(fields) == 1
        assert fields[0].key == "tn0112"
        assert len(fields[0].children) == 1
        assert fields[0].children[0].key == "Rtd"
        assert fields[0].children[0].value == "228.200"

    def test_raw_preserved(self) -> None:
        """Raw segment string is preserved on grouped fields."""
        cp = "tn0112-Rtd=228.200,tn0112-Flag=N"
        fields = self.parser.parse_grouped(cp)

        assert fields[0].raw == "tn0112-Rtd=228.200,tn0112-Flag=N"

    def test_three_attributes_same_factor(self) -> None:
        """Three attributes for same factor are all grouped."""
        cp = "w01001-Rtd=12.5,w01001-Flag=N,w01001-Min=10.0"
        fields = self.parser.parse_grouped(cp)

        assert len(fields) == 1
        assert fields[0].key == "w01001"
        assert len(fields[0].children) == 3
        attrs = {c.key: c.value for c in fields[0].children}
        assert attrs == {"Rtd": "12.5", "Flag": "N", "Min": "10.0"}


# ---------------------------------------------------------------------------
# CPField.to_dict() tests
# ---------------------------------------------------------------------------


class TestCPFieldToDict:
    """Tests for CPField.to_dict() JSON serialization."""

    def test_simple_field(self) -> None:
        """Single field serializes to {key: value}."""
        f = CPField(key="w01001-Rtd", value="12.5")
        d = f.to_dict()
        assert d == {"w01001-Rtd": "12.5"}

    def test_empty_value(self) -> None:
        """Empty value returns empty string."""
        f = CPField(key="Marker", value="")
        d = f.to_dict()
        assert d == {"Marker": ""}

    def test_with_children(self) -> None:
        """Field with children serializes to {key: {attr: value}}."""
        f = CPField(
            key="tn0112",
            children=[
                CPField(key="Rtd", value="228.200"),
                CPField(key="Flag", value="N"),
            ],
        )
        d = f.to_dict()
        assert d == {"tn0112": {"Rtd": "228.200", "Flag": "N"}}

    def test_json_roundtrip(self) -> None:
        """to_dict output is valid JSON."""
        fields = [
            CPField(key="DataTime", value="20261118134500"),
            CPField(
                key="tn0112",
                children=[
                    CPField(key="Rtd", value="228.200"),
                    CPField(key="Flag", value="N"),
                ],
            ),
        ]
        data = [f.to_dict() for f in fields]
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        loaded = json.loads(json_str)
        assert loaded[0] == {"DataTime": "20261118134500"}
        assert loaded[1] == {"tn0112": {"Rtd": "228.200", "Flag": "N"}}
