"""Tests for CP field parsing."""

from __future__ import annotations

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
        fields = self.parser.parse(
            "a01007-Avg=-99.0;a01008-Avg=-99;a05024-Avg=-99.00"
        )
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
        fields = self.parser.parse(
            "PNO=000000004;DataTime=20260902082000;RtdInterval=300"
        )
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
