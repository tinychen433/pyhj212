"""Tests for the message encoder."""

from __future__ import annotations

import pytest

from pyhj212.exceptions import EncodeError
from pyhj212.models.header import Header
from pyhj212.models.message import Message
from pyhj212.protocol.encoder import Encoder
from pyhj212.protocol.parser import Parser

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Real-world CN=1062 (set RtdInterval) message
EXPECTED_RAW = (
    "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
    "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
    "1C80\r\n"
)
"""Original device message for reference."""

# ---------------------------------------------------------------------------
# Valid encoding tests
# ---------------------------------------------------------------------------


class TestEncodeMessage:
    """Tests for Encoder.encode() with Message objects."""

    def setup_method(self) -> None:
        self.encoder = Encoder()
        self.parser = Parser()

    def test_encode_cn1062_message(self) -> None:
        """Encode a CN=1062 (set RtdInterval) message."""
        header = Header(
            flag="5", pno="",
            qn="20160801085857223", st="32", cn="1062", pw="100000",
            mn="010000A8900016F000169DC0",
        )
        message = Message(header=header, data="RtdInterval=30")
        raw = self.encoder.encode(message)

        # Verify format
        assert raw.startswith("##")
        assert raw.endswith("\r\n")

        # Verify roundtrip
        parsed = self.parser.parse(raw)
        assert parsed.header.cn == "1062"
        assert parsed.header.qn == "20160801085857223"
        assert parsed.header.mn == "010000A8900016F000169DC0"
        assert parsed.header.flag == "5"
        assert parsed.data == "RtdInterval=30"

    def test_encode_generates_valid_crc(self) -> None:
        """Encoded message CRC is valid after roundtrip."""
        header = Header(
            flag="5", pno="",
            qn="20160801085857223", st="32", cn="1062", pw="100000",
            mn="010000A8900016F000169DC0",
        )
        message = Message(header=header, data="RtdInterval=30")
        raw = self.encoder.encode(message)

        # Extract CRC: last 4 chars before \r\n
        crc_in_msg = raw[-6:-2]
        # Data for CRC = everything between length and CRC
        data_for_crc = raw[6:-6]  # skip ##LLLL and CRC\r\n

        from pyhj212.protocol.checksum import calculate_crc
        assert calculate_crc(data_for_crc) == int(crc_in_msg, 16)

    def test_encode_generates_correct_length(self) -> None:
        """Encoded message length field matches actual data length."""
        header = Header(
            flag="5", pno="",
            qn="20160801085857223", st="32", cn="1062", pw="100000",
            mn="010000A8900016F000169DC0",
        )
        message = Message(header=header, data="RtdInterval=30")
        raw = self.encoder.encode(message)

        declared_length = int(raw[2:6])
        # Content between ##LLLL and CRC\r\n = length chars of data
        content = raw[6:-6]  # strip ##0101 prefix and CRC\r\n suffix
        assert declared_length == len(content)

    def test_encode_empty_data(self) -> None:
        """Message with empty data encodes correctly."""
        header = Header(flag="0", pno="", cn="2011", pw="123456")
        message = Message(header=header)
        raw = self.encoder.encode(message)

        # Encoder adds && separator even with empty body
        assert "&&" in raw

        parsed = self.parser.parse(raw)
        assert parsed.header.cn == "2011"
        assert parsed.data == ""

    def test_encode_with_cp_data(self) -> None:
        """Message with CP data encodes correctly."""
        header = Header(
            flag="5", pno="4",
            qn="20260902083001000", st="31", cn="2051", pw="123456",
            mn="YSRDAQ07ST00002713",
        )
        message = Message(
            header=header,
            data="PNO=000000004;DataTime=20260902082000;RtdInterval=300",
        )
        raw = self.encoder.encode(message)

        parsed = self.parser.parse(raw)
        assert "PNO=000000004" in parsed.data
        assert "DataTime=20260902082000" in parsed.data

    def test_encode_with_negative_values(self) -> None:
        """Message with negative values encodes correctly."""
        header = Header(flag="5", pno="", cn="2051", pw="123456")
        message = Message(
            header=header,
            data="ys0018-Avg=-99.000;a01006-Rtd=-99.000",
        )
        raw = self.encoder.encode(message)

        parsed = self.parser.parse(raw)
        assert "ys0018-Avg=-99.000" in parsed.data

    def test_encode_preserves_crc_format(self) -> None:
        """CRC in encoded message is 4-digit uppercase hex."""
        header = Header(flag="0", pno="", cn="2011", pw="000000")
        message = Message(header=header, data="test=1")
        raw = self.encoder.encode(message)

        # CRC is 4 chars before \r\n
        crc = raw[-6:-2]
        assert len(crc) == 4
        assert crc == crc.upper()
        int(crc, 16)  # valid hex

    def test_encode_length_is_four_digits(self) -> None:
        """Length field is always 4 digits, zero-padded."""
        header = Header(flag="0", pno="", cn="2011", pw="000000")
        message = Message(header=header, data="x")
        raw = self.encoder.encode(message)

        length_str = raw[2:6]
        assert len(length_str) == 4
        assert length_str.isdigit()

    # -- Encode errors --

    def test_encode_data_too_long(self) -> None:
        """Data exceeding 9999 chars raises EncodeError."""
        header = Header(flag="0", pno="", cn="2011", pw="000000")
        message = Message(header=header, data="x" * 9998)
        # header_str + && + 9998 chars > 9999
        with pytest.raises(EncodeError) as exc_info:
            self.encoder.encode(message)
        assert "exceeds" in str(exc_info.value).lower()
