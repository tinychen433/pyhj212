"""Message parser for HJ 212-2017 protocol."""

from __future__ import annotations

from pyhj212.constants import START_DELIMITER
from pyhj212.exceptions import ParseError
from pyhj212.models.header import Header
from pyhj212.models.message import Message


class Parser:
    """Parses raw HJ 212-2017 message strings into structured objects.

    Message format: ``##LLLL<Data><CRC>\\r\\n``

    - ``##``: Start delimiter (2 chars)
    - ``LLLL``: Data length (4 digits, zero-padded)
    - ``<Data>``: Header + ``&&`` + CP data (LLLL chars)
    - ``<CRC>``: CRC-16 checksum (4 hex chars, uppercase)
    - ``\\r\\n``: End delimiter

    The parser handles the complete message format:
    - Start delimiter (##)
    - Data length field
    - Header fields
    - Data content with CP fields
    - CRC checksum
    - End delimiter (\\r\\n)
    """

    def parse(self, raw: str) -> Message:
        """Parse a raw HJ 212-2017 message string.

        Args:
            raw: The complete raw message string.

        Returns:
            A Message object with parsed components.

        Raises:
            ParseError: If the message format is invalid.
        """
        if not raw.startswith(START_DELIMITER):
            raise ParseError(
                f"Message must start with '{START_DELIMITER}'",
                position=0,
            )

        # After ##: LLLL<Data><CRC>\r\n
        payload = raw[len(START_DELIMITER):]

        # Extract declared length (4 digits)
        if len(payload) < 4:
            raise ParseError("Message too short: missing length field", position=2)

        try:
            declared_length = int(payload[:4])
        except ValueError as exc:
            raise ParseError(
                f"Invalid length field: {payload[:4]!r}",
                position=2,
            ) from exc

        # Full content = length + data + crc
        # Data starts at position 4, CRC is last 4 chars before \r\n
        min_len = 4 + declared_length + 4 + 2  # LLLL + data + CRC + \r\n
        if len(payload) < min_len:
            raise ParseError(
                f"Message too short: need {min_len}, got {len(payload)}",
            )

        data_section = payload[4 : 4 + declared_length]
        crc_str = payload[4 + declared_length : 4 + declared_length + 4]

        # Parse header (before first &&)
        header_end = data_section.find("&&")
        if header_end == -1:
            raise ParseError("Missing data separator '&&'")

        header_str = data_section[:header_end]
        header = self._parse_header(header_str)

        # Extract data body (between first && and optional trailing &&)
        cp_data = data_section[header_end + 2 :]
        # Strip trailing && if present (closing delimiter before CRC)
        if cp_data.endswith("&&"):
            cp_data = cp_data[:-2]

        return Message(
            header=header,
            data=cp_data,
            raw=raw,
            crc=crc_str,
        )

    def _parse_header(self, header_str: str) -> Header:
        """Parse header fields from semicolon-separated string.

        Args:
            header_str: Semicolon-separated header fields.

        Returns:
            A Header dataclass with parsed fields.

        Raises:
            ParseError: If required fields are missing.
        """
        fields: dict[str, str] = {}
        for part in header_str.split(";"):
            if "=" not in part:
                raise ParseError(f"Invalid header field: {part!r}")
            key, value = part.split("=", 1)
            fields[key] = value

        cn = fields.get("CN", "")
        pw = fields.get("PW", "")

        if not cn:
            raise ParseError("CN (command number) is required")

        return Header(
            qn=fields.get("QN", ""),
            st=fields.get("ST", ""),
            cn=cn,
            pw=pw,
            mn=fields.get("MN", ""),
            flag=fields.get("Flag", ""),
            pno=fields.get("PNO", ""),
            raw=header_str,
        )
