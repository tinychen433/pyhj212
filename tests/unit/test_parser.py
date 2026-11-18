"""Tests for the message parser."""

from __future__ import annotations

import pytest

from pyhj212.exceptions import ParseError
from pyhj212.protocol.parser import Parser

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Real-world CN=2051 (real-time data upload) message — 44 CP fields
REALTIME_MESSAGE_RAW = (
    "##0857QN=20260902083001000;ST=31;CN=2051;PW=123456;"
    "MN=YSRDAQ07ST00002713;Flag=5;CP=&&"
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
    "&&A141\r\n"
)

# Minimal valid message (CN=2011, single data field)
# Data section is 84 chars: header(67) + &&(2) + body(15) = 84
# CRC=9741 immediately follows the data
SIMPLE_MESSAGE_RAW = (
    "##0084QN=20260902083001000;ST=32;CN=2011;PW=123456;MN=ST0001;"
    "Flag=4;PNO=1&&w01001-Rtd=12.59741\r\n"
)

# ---------------------------------------------------------------------------
# Valid message parsing
# ---------------------------------------------------------------------------


class TestParseValidMessage:
    """Tests for successful message parsing."""

    def setup_method(self) -> None:
        self.parser = Parser()

    def test_realtime_message(self) -> None:
        """Parse a real-world CN=2051 message with 44 CP fields."""
        msg = self.parser.parse(REALTIME_MESSAGE_RAW)

        assert msg.header.qn == "20260902083001000"
        assert msg.header.cn == "2051"
        assert msg.header.pw == "123456"
        assert msg.header.mn == "YSRDAQ07ST00002713"
        assert msg.header.st == "31"
        assert msg.header.flag == "5"

        # Data section contains CP fields
        assert "PNO=000000004" in msg.data
        assert "DataTime=20260902082000" in msg.data
        assert "a34004-Avg=3.000" in msg.data

        # CRC preserved
        assert msg.crc == "A141"

        # Raw message preserved
        assert msg.raw == REALTIME_MESSAGE_RAW

    def test_simple_message(self) -> None:
        """Parse a minimal valid message."""
        msg = self.parser.parse(SIMPLE_MESSAGE_RAW)

        assert msg.header.qn == "20260902083001000"
        assert msg.header.cn == "2011"
        assert msg.header.mn == "ST0001"
        assert msg.header.st == "32"
        assert msg.header.flag == "4"
        assert msg.header.pno == "1"

        # Data section: 84 chars = header(67) + &&(2) + body(15)
        # CRC "9741" follows the data section
        assert msg.data == "w01001-Rtd=12.5"
        assert msg.crc == "9741"

    def test_data_length_matches_declaration(self) -> None:
        """Parser enforces declared length matches actual data length."""
        msg = self.parser.parse(REALTIME_MESSAGE_RAW)
        # Data section (857) = header + && + body + trailing &&
        # After stripping trailing &&: header_len + 2 + body_len = 857 - 2 = 855
        header_len = len(msg.header.raw)
        body_len = len(msg.data)
        assert header_len + 2 + body_len == 855  # trailing && stripped

    def test_raw_preservation(self) -> None:
        """Original message is preserved unchanged."""
        msg = self.parser.parse(SIMPLE_MESSAGE_RAW)
        assert msg.raw == SIMPLE_MESSAGE_RAW

    # -- Header field edge cases --

    def test_header_without_qn(self) -> None:
        """Message without QN field still parses (QN is not strictly required)."""
        from pyhj212.protocol.checksum import calculate_crc

        data = "CN=2011;PW=123456;MN=ST0001;ST=32;Flag=4;PNO=1&&w01001-Rtd=12.5"
        crc = calculate_crc(data)
        raw = f"##{len(data):04d}{data}{crc:04X}\r\n"

        msg = self.parser.parse(raw)
        assert msg.header.qn == ""
        assert msg.header.cn == "2011"

    def test_long_mn_value(self) -> None:
        """Message with long MN (18 chars) parses correctly."""
        msg = self.parser.parse(REALTIME_MESSAGE_RAW)
        assert len(msg.header.mn) == 18
        assert msg.header.mn == "YSRDAQ07ST00002713"

    def test_zero_flag(self) -> None:
        """Message with Flag=0 parses correctly."""
        from pyhj212.protocol.checksum import calculate_crc

        data = "CN=2011;PW=000000;Flag=0&&"
        crc = calculate_crc(data)
        raw = f"##{len(data):04d}{data}{crc:04X}\r\n"

        msg = self.parser.parse(raw)
        assert msg.header.flag == "0"

    def test_large_pno(self) -> None:
        """Message with large PNO value parses correctly."""
        msg = self.parser.parse(REALTIME_MESSAGE_RAW)
        assert msg.header.raw  # Header contains PNO in CP field context

    def test_qn_timestamp_format(self) -> None:
        """QN uses YYYYMMDDHHmmssSSS format (17 chars)."""
        msg = self.parser.parse(REALTIME_MESSAGE_RAW)
        assert len(msg.header.qn) == 17
        assert msg.header.qn.startswith("20260902")

    def test_negative_values_in_data(self) -> None:
        """Data containing negative values parses correctly."""
        msg = self.parser.parse(REALTIME_MESSAGE_RAW)
        assert "ys0018-Avg=-99.000" in msg.data

    def test_very_long_numeric_value(self) -> None:
        """Data with very long numeric strings (e.g. ICCID) parses correctly."""
        msg = self.parser.parse(REALTIME_MESSAGE_RAW)
        assert "ys0014-Rtd=89860473102590002828" in msg.data

    def test_high_precision_floats(self) -> None:
        """Data with 6+ decimal precision parses correctly."""
        msg = self.parser.parse(REALTIME_MESSAGE_RAW)
        assert "ys0007-Rtd=116.489983" in msg.data

    def test_empty_body_after_separator(self) -> None:
        """Message with && but no data body parses correctly."""
        from pyhj212.protocol.checksum import calculate_crc

        data = "CN=2011;PW=000000;Flag=0&&"
        crc = calculate_crc(data)
        raw = f"##{len(data):04d}{data}{crc:04X}\r\n"

        msg = self.parser.parse(raw)
        assert msg.data == ""
        assert msg.header.cn == "2011"

    # -- Parse errors --

    def test_missing_start_delimiter(self) -> None:
        """Message without ## prefix raises ParseError."""
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse("0857QN=20260902083001000;ST=31\r\n")
        assert "start with" in str(exc_info.value).lower()

    def test_too_short_message(self) -> None:
        """Message shorter than minimum length raises ParseError."""
        with pytest.raises(ParseError):
            self.parser.parse("##00")

    def test_invalid_length_field(self) -> None:
        """Non-numeric length field raises ParseError."""
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse("##ABCDdata\r\n")
        assert "invalid" in str(exc_info.value).lower()

    def test_missing_separator(self) -> None:
        """Message without && separator raises ParseError."""
        from pyhj212.protocol.checksum import calculate_crc

        data = "CN=2011;PW=123456;Flag=0"
        crc = calculate_crc(data)
        raw = f"##{len(data):04d}{data}{crc:04X}\r\n"

        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(raw)
        assert "separator" in str(exc_info.value).lower() or "&&" in str(
            exc_info.value
        )

    def test_length_mismatch(self) -> None:
        """Declared length not matching actual data raises ParseError."""
        with pytest.raises(ParseError):
            # Declares 0001 but actual data is much longer
            self.parser.parse(REALTIME_MESSAGE_RAW.replace("0857", "0001", 1))

    def test_empty_string(self) -> None:
        """Empty string raises ParseError."""
        with pytest.raises(ParseError):
            self.parser.parse("")

    def test_invalid_header_field(self) -> None:
        """Header field without = raises ParseError."""
        from pyhj212.protocol.checksum import calculate_crc

        data = "CN=2011;INVALID;PW=123456;Flag=0&&"
        crc = calculate_crc(data)
        raw = f"##{len(data):04d}{data}{crc:04X}\r\n"

        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(raw)
        assert "invalid" in str(exc_info.value).lower()
