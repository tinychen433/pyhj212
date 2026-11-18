"""Protocol validator for HJ 212-2017 messages."""

from __future__ import annotations

from pyhj212.constants import END_DELIMITER, START_DELIMITER
from pyhj212.models.message import Message
from pyhj212.models.validation import ValidationResult
from pyhj212.protocol.checksum import verify_crc


class Validator:
    """Validates HJ 212-2017 messages for protocol compliance.

    Checks include:
    - Message format and delimiters
    - Data length field accuracy
    - CRC checksum verification
    - Required header fields
    - Data field constraints
    """

    def validate(self, raw: str) -> ValidationResult:
        """Validate a raw HJ 212-2017 message.

        Args:
            raw: The raw message string to validate.

        Returns:
            ValidationResult indicating validity and any errors/warnings.
        """
        result = ValidationResult()

        if not raw.startswith(START_DELIMITER):
            result.add_error(
                f"Message must start with '{START_DELIMITER}'"
            )
            return result

        if not raw.endswith(END_DELIMITER):
            result.add_error(
                f"Message must end with {END_DELIMITER!r}"
            )
            return result

        # Extract content: strip ## prefix and \r\n suffix
        content = raw[len(START_DELIMITER) : -len(END_DELIMITER)]

        # Extract and validate length
        try:
            declared_length = int(content[:4])
        except ValueError:
            result.add_error("Invalid length field")
            return result

        actual_content = content[4:-4]  # Skip length and CRC
        if len(actual_content) != declared_length:
            result.add_error(
                f"Length mismatch: declared {declared_length}, actual {len(actual_content)}",
            )

        # Validate CRC
        crc_str = content[-4:]
        try:
            expected_crc = int(crc_str, 16)
        except ValueError:
            result.add_error(f"Invalid CRC format: {crc_str!r}")
            return result

        if not verify_crc(actual_content, expected_crc):
            result.add_error("CRC verification failed")

        return result

    def validate_message(self, message: Message) -> ValidationResult:
        """Validate a parsed Message object.

        Args:
            message: The parsed Message to validate.

        Returns:
            ValidationResult indicating validity and any errors/warnings.
        """
        result = ValidationResult()

        if not message.header.cn:
            result.add_error("CN (command number) is required")

        if message.data and len(message.data) > 9999:
            result.add_error("Data length exceeds maximum of 9999")

        return result
