"""Message encoder for HJ 212-2017 protocol."""

from __future__ import annotations

from pyhj212.constants import END_DELIMITER, START_DELIMITER
from pyhj212.exceptions import EncodeError
from pyhj212.models.message import Message
from pyhj212.protocol.checksum import calculate_crc


class Encoder:
    """Encodes HJ 212-2017 Message objects into raw protocol strings.

    The encoder handles the complete message format:
    - Start delimiter (##)
    - Data length field (4 digits, zero-padded)
    - Header fields
    - Data content with CP fields
    - CRC checksum (4 hex digits, uppercase)
    - End delimiter (\\r\\n)
    """

    def encode(self, message: Message) -> str:
        """Encode a Message object into a raw HJ 212-2017 string.

        Args:
            message: The Message object to encode.

        Returns:
            The complete encoded message string.

        Raises:
            EncodeError: If the message cannot be encoded.
        """
        header_str = message.header.to_string()
        body = message.data
        content = f"{header_str}&&{body}" if body else header_str

        crc = calculate_crc(content)
        crc_str = f"{crc:04X}"

        length = len(content)
        if length > 9999:
            raise EncodeError(
                f"Data length {length} exceeds maximum of 9999",
            )

        length_str = f"{length:04d}"

        raw = f"{START_DELIMITER}{length_str}{content}{crc_str}{END_DELIMITER}"
        return raw
