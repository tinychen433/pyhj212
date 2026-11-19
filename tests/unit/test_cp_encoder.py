"""Tests for CP field encoding."""

from __future__ import annotations

from pyhj212.cp.encoder import CPEncoder
from pyhj212.cp.models import CPField
from pyhj212.cp.parser import CPParser

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Valid CP encoding tests
# ---------------------------------------------------------------------------


class TestCPEncode:
    """Tests for CPEncoder.encode() with CPField objects."""

    def setup_method(self) -> None:
        self.encoder = CPEncoder()
        self.parser = CPParser()

    def test_encode_realtime_cp_data(self) -> None:
        """Encode and decode 44 CP fields roundtrip."""
        fields = self.parser.parse(REALTIME_CP_DATA)
        encoded = self.encoder.encode(fields)
        decoded = self.parser.parse(encoded)

        assert len(decoded) == len(fields)
        for orig, enc in zip(fields, decoded):
            assert orig.key == enc.key
            assert orig.value == enc.value

    def test_encode_single_field(self) -> None:
        """Encode a single key=value field."""
        fields = [CPField(key="w01001-Rtd", value="12.5")]
        assert self.encoder.encode(fields) == "w01001-Rtd=12.5"

    def test_encode_multiple_fields(self) -> None:
        """Encode multiple fields with semicolon separator."""
        fields = [
            CPField(key="a", value="1"),
            CPField(key="b", value="2"),
            CPField(key="c", value="3"),
        ]
        assert self.encoder.encode(fields) == "a=1;b=2;c=3"

    def test_encode_field_without_value(self) -> None:
        """Field without value is encoded as key only."""
        fields = [CPField(key="FlagMarker")]
        assert self.encoder.encode(fields) == "FlagMarker"

    def test_encode_mixed_fields(self) -> None:
        """Mixed fields with and without values."""
        fields = [
            CPField(key="a", value="1"),
            CPField(key="b"),
            CPField(key="c", value="3"),
        ]
        assert self.encoder.encode(fields) == "a=1;b;c=3"

    def test_encode_empty_list(self) -> None:
        """Empty list produces empty string."""
        assert self.encoder.encode([]) == ""

    def test_encode_negative_values(self) -> None:
        """Negative numeric values are preserved."""
        fields = [CPField(key="ys0018-Avg", value="-99.000")]
        assert self.encoder.encode(fields) == "ys0018-Avg=-99.000"

    def test_encode_very_long_value(self) -> None:
        """Very long values (20+ digits) are preserved."""
        fields = [CPField(key="ys0014-Rtd", value="89860473102590002828")]
        encoded = self.encoder.encode(fields)
        assert "89860473102590002828" in encoded

    def test_encode_varied_decimal_precision(self) -> None:
        """Different decimal precision is preserved exactly."""
        fields = [
            CPField(key="a", value="-99.0"),
            CPField(key="b", value="-99"),
            CPField(key="c", value="-99.00"),
        ]
        assert self.encoder.encode(fields) == "a=-99.0;b=-99;c=-99.00"

    def test_encode_roundtrip_with_parser(self) -> None:
        """Encode → parse produces identical CPField list."""
        original = [
            CPField(key="PNO", value="000000004"),
            CPField(key="DataTime", value="20260902082000"),
            CPField(key="RtdInterval", value="300"),
        ]
        encoded = self.encoder.encode(original)
        decoded = self.parser.parse(encoded)

        assert len(decoded) == len(original)
        for orig, dec in zip(original, decoded):
            assert orig.key == dec.key
            assert orig.value == dec.value

    def test_encode_raw_preservation(self) -> None:
        """Encoded output matches expected format."""
        fields = [
            CPField(key="RtdInterval", value="30"),
        ]
        result = self.encoder.encode(fields)
        assert result == "RtdInterval=30"
        assert ";" not in result  # no trailing separator

    def test_encode_grouped_fields(self) -> None:
        """Grouped fields with children encode to factor-attr=value format."""
        fields = [
            CPField(
                key="tn0112",
                children=[
                    CPField(key="Rtd", value="228.200"),
                    CPField(key="Flag", value="N"),
                ],
            ),
        ]
        assert self.encoder.encode(fields) == "tn0112-Rtd=228.200,tn0112-Flag=N"

    def test_encode_mixed_flat_and_grouped(self) -> None:
        """Flat and grouped fields coexist in encoded output."""
        fields = [
            CPField(key="DataTime", value="20261118134500"),
            CPField(
                key="tn0112",
                children=[
                    CPField(key="Rtd", value="228.200"),
                    CPField(key="Flag", value="N"),
                ],
            ),
            CPField(key="RtdInterval", value="300"),
        ]
        result = self.encoder.encode(fields)
        assert result == "DataTime=20261118134500;tn0112-Rtd=228.200,tn0112-Flag=N;RtdInterval=300"

    def test_encode_grouped_roundtrip(self) -> None:
        """parse_grouped → encode → parse_grouped roundtrip."""
        cp = "DataTime=20261118134500;tn0112-Rtd=228.200,tn0112-Flag=N;tn0110-Rtd=229.100,tn0110-Flag=N"
        original = self.parser.parse_grouped(cp)
        encoded = self.encoder.encode(original)
        decoded = self.parser.parse_grouped(encoded)

        assert len(decoded) == len(original)
        for orig, dec in zip(original, decoded):
            assert orig.key == dec.key
            for oc, dc in zip(orig.children, dec.children):
                assert oc.key == dc.key
                assert oc.value == dc.value
