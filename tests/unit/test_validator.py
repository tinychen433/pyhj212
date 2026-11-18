"""Tests for the protocol validator."""

from __future__ import annotations

from pyhj212.models.header import Header
from pyhj212.models.message import Message
from pyhj212.protocol.validator import Validator

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_MESSAGE_RAW = (
    "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
    "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
    "1C80\r\n"
)
"""Real-world HJ212-2017 CN=1062 (set RtdInterval) message.

CRC=1C80 verified against actual device data using the correct
HJ212 CRC algorithm: per-byte (crc >> 8) ^ byte with polynomial
0xA001 and initial value 0xFFFF.
"""

VALID_SHORT_MESSAGE_RAW = (
    "##0084QN=20260902083001000;ST=32;CN=2011;PW=123456;MN=ST0001;"
    "Flag=4;PNO=1&&w01001-Rtd=12.59741\r\n"
)
"""Minimal valid message for quick validation tests."""

# ---------------------------------------------------------------------------
# Valid message tests
# ---------------------------------------------------------------------------


class TestValidateRawMessage:
    """Tests for Validator.validate() with raw message strings."""

    def setup_method(self) -> None:
        self.validator = Validator()

    def test_valid_message_passes(self) -> None:
        """A well-formed message with correct CRC passes validation."""
        result = self.validator.validate(VALID_MESSAGE_RAW)
        assert result.is_valid
        assert result.errors == []

    def test_valid_short_message_passes(self) -> None:
        """A shorter valid message also passes."""
        result = self.validator.validate(VALID_SHORT_MESSAGE_RAW)
        assert result.is_valid
        assert result.errors == []

    # -- Format errors --

    def test_missing_start_delimiter(self) -> None:
        """Message without ## prefix fails format validation."""
        result = self.validator.validate(
            "0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
            "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
            "0759\r\n"
        )
        assert not result.is_valid
        assert len(result.errors) >= 1

    def test_missing_end_delimiter(self) -> None:
        """Message without \\r\\n suffix fails format validation."""
        result = self.validator.validate(
            "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
            "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
            "0759"
        )
        assert not result.is_valid
        assert len(result.errors) >= 1

    def test_empty_string(self) -> None:
        """Empty string fails validation."""
        result = self.validator.validate("")
        assert not result.is_valid

    # -- Length field errors --

    def test_invalid_length_field(self) -> None:
        """Non-numeric length field triggers an error."""
        result = self.validator.validate("##ABCDdataFFFF\r\n")
        assert not result.is_valid
        assert any("length" in e.lower() for e in result.errors)

    def test_length_mismatch(self) -> None:
        """Declared length not matching actual data length."""
        # Declares 0001 but actual data is much longer
        result = self.validator.validate(VALID_MESSAGE_RAW.replace("0101", "0001", 1))
        assert not result.is_valid
        assert any("mismatch" in e.lower() for e in result.errors)

    # -- CRC errors --

    def test_wrong_crc(self) -> None:
        """Message with incorrect CRC fails validation."""
        # Flip the last digit of the CRC
        bad_crc_msg = VALID_SHORT_MESSAGE_RAW[:-5] + "FFFF\r\n"
        result = self.validator.validate(bad_crc_msg)
        assert not result.is_valid
        assert "CRC verification failed" in result.errors

    def test_invalid_crc_format(self) -> None:
        """CRC field containing non-hex characters fails."""
        result = self.validator.validate("##0004test&&ZZZZ\r\n")
        assert not result.is_valid


class TestValidateMessageObject:
    """Tests for Validator.validate_message() with parsed Message objects."""

    def setup_method(self) -> None:
        self.validator = Validator()

    def test_valid_message_object(self) -> None:
        """A properly constructed Message passes validation."""
        header = Header(
            qn="20260902083001000",
            cn="2011",
            pw="123456",
            mn="ST0001",
            st="32",
            flag="4",
            pno="1",
        )
        message = Message(header=header, data="w01001-Rtd=12.5")
        result = self.validator.validate_message(message)
        assert result.is_valid

    def test_missing_cn(self) -> None:
        """Message without CN field fails validation."""
        header = Header(flag="", pno="", qn="", cn="", pw="123456")
        message = Message(header=header)
        result = self.validator.validate_message(message)
        assert not result.is_valid
        assert any("CN" in e for e in result.errors)

    def test_data_exceeds_maximum(self) -> None:
        """Data longer than 9999 characters fails validation."""
        header = Header(flag="", pno="", qn="", cn="2011", pw="123456")
        message = Message(header=header, data="x" * 10000)
        result = self.validator.validate_message(message)
        assert not result.is_valid
        assert any("9999" in e for e in result.errors)
