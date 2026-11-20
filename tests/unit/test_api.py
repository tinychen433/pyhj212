"""Tests for the high-level convenience API."""

from __future__ import annotations

import pytest

from pyhj212 import (
    CPField,
    Header,
    Message,
    encode,
    encode_cp,
    parse,
    parse_cp,
    validate,
)
from pyhj212.exceptions import ParseError

# ---------------------------------------------------------------------------
# Test parse()
# ---------------------------------------------------------------------------


class TestParse:
    def test_parse_real_message(self) -> None:
        """Parse a real-world message and verify header fields."""
        raw = (
            "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
            "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
            "1C80\r\n"
        )
        msg = parse(raw)
        assert isinstance(msg, Message)
        assert msg.header.cn == "1062"
        assert msg.header.mn == "010000A8900016F000169DC0"
        assert msg.data == "RtdInterval=30"
        assert msg.crc == "1C80"

    def test_parse_auto_parses_cp_fields(self) -> None:
        """Message.cp_fields returns grouped CPField objects."""
        raw = (
            "##0084QN=20260902083001000;ST=32;CN=2011;PW=123456;"
            "MN=ST0001;Flag=4;PNO=1&&w01001-Rtd=12.5&&9741\r\n"
        )
        msg = parse(raw)
        fields = msg.cp_fields
        assert len(fields) == 1
        assert fields[0].key == "w01001"
        assert fields[0].children[0].key == "Rtd"
        assert fields[0].children[0].value == "12.5"

    def test_parse_empty_data(self) -> None:
        """Message with empty CP data returns empty cp_fields."""
        # Use encode to create a valid empty-data message
        header = Header(cn="1062", pw="100000", mn="ST0001")
        raw = encode(header, "")
        msg = parse(raw)
        assert msg.data == ""
        assert msg.cp_fields == []

    def test_parse_error_propagates(self) -> None:
        """Invalid input raises ParseError."""
        with pytest.raises(ParseError):
            parse("")


# ---------------------------------------------------------------------------
# Test encode()
# ---------------------------------------------------------------------------


class TestEncode:
    def test_encode_with_header_object(self) -> None:
        """Encode with Header object."""
        header = Header(
            qn="20160801085857223", st="32", cn="1062", pw="100000",
            mn="010000A8900016F000169DC0", flag="5",
        )
        raw = encode(header, "RtdInterval=30")
        assert raw.startswith("##")
        assert raw.endswith("\r\n")

    def test_encode_with_dict_header(self) -> None:
        """Encode with dict header (case-insensitive keys)."""
        raw = encode(
            header={"CN": "1062", "PW": "100000", "MN": "ST0001"},
            data="RtdInterval=30",
        )
        assert "CN=1062" in raw
        assert "PW=100000" in raw

    def test_encode_with_list_of_dicts(self) -> None:
        """Encode with list[dict] data (to_dict format)."""
        header = Header(cn="1062", pw="100000", mn="ST0001")
        raw = encode(
            header,
            data=[
                {"DataTime": "20261118134500"},
                {"tn0112": {"Rtd": "228.200", "Flag": "N"}},
            ],
        )
        assert "DataTime=20261118134500" in raw
        assert "tn0112-Rtd=228.200" in raw
        assert "tn0112-Flag=N" in raw

    def test_encode_dict_data_roundtrip(self) -> None:
        """parse → extract cp_fields dicts → encode → parse roundtrip."""
        raw_in = (
            "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
            "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
            "1C80\r\n"
        )
        msg = parse(raw_in)
        dicts = [f.to_dict() for f in msg.cp_fields]
        raw_out = encode(msg.header, dicts)
        reparsed = parse(raw_out)
        assert reparsed.header.cn == msg.header.cn
        assert reparsed.data == msg.data


# ---------------------------------------------------------------------------
# Test validate()
# ---------------------------------------------------------------------------


class TestValidate:
    def test_valid_message(self) -> None:
        """A well-formed message passes validation."""
        raw = (
            "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
            "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
            "1C80\r\n"
        )
        result = validate(raw)
        assert result.is_valid

    def test_invalid_message(self) -> None:
        """Invalid input fails validation."""
        result = validate("not a valid message")
        assert not result.is_valid


# ---------------------------------------------------------------------------
# Test parse_cp() / encode_cp()
# ---------------------------------------------------------------------------


class TestParseCp:
    def test_parse_cp_flat(self) -> None:
        """Parse flat CP fields."""
        fields = parse_cp("PNO=000000004;DataTime=20260902082000")
        assert len(fields) == 2
        assert fields[0].key == "PNO"
        assert fields[1].key == "DataTime"

    def test_parse_cp_grouped(self) -> None:
        """Parse grouped CP fields (factor code + attributes)."""
        fields = parse_cp("tn0112-Rtd=228.200,tn0112-Flag=N")
        assert len(fields) == 1
        assert fields[0].key == "tn0112"
        assert len(fields[0].children) == 2

    def test_parse_cp_empty(self) -> None:
        """Empty string returns empty list."""
        assert parse_cp("") == []


class TestEncodeCp:
    def test_encode_cp_roundtrip(self) -> None:
        """encode_cp(parse_cp(x)) == x for flat fields."""
        original = "PNO=000000004;DataTime=20260902082000"
        fields = parse_cp(original)
        assert encode_cp(fields) == original

    def test_encode_cp_grouped(self) -> None:
        """Encode grouped fields back to grouped format."""
        fields = parse_cp("tn0112-Rtd=228.200,tn0112-Flag=N")
        result = encode_cp(fields)
        assert "tn0112-Rtd=228.200" in result
        assert "tn0112-Flag=N" in result

    def test_encode_cp_single_field(self) -> None:
        """Encode a single field."""
        fields = [CPField(key="RtdInterval", value="30")]
        assert encode_cp(fields) == "RtdInterval=30"
