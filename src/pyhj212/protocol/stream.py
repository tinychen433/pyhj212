"""TCP stream decoder for HJ 212-2017 protocol."""

from __future__ import annotations

from pyhj212.constants import END_DELIMITER, START_DELIMITER
from pyhj212.exceptions import ParseError
from pyhj212.models.message import Message
from pyhj212.protocol.parser import Parser


class StreamDecoder:
    """Decodes HJ 212-2017 messages from a TCP byte stream.

    Handles:
    - Message framing with start/end delimiters
    - Stream concatenation (multiple messages in one buffer)
    - Message fragmentation (partial messages across reads)
    """

    def __init__(self) -> None:
        """Initialize the stream decoder with an empty buffer."""
        self._buffer = ""
        self._parser = Parser()

    def feed(self, data: bytes) -> list[Message]:
        """Feed raw bytes into the decoder and return complete messages.

        Args:
            data: Raw bytes from the TCP stream.

        Returns:
            List of fully parsed Message objects.
        """
        self._buffer += data.decode("ascii", errors="replace")
        messages = self._extract_messages()
        return messages

    def _extract_messages(self) -> list[Message]:
        """Extract complete messages from the buffer.

        Returns:
            List of parsed Message objects.
        """
        messages: list[Message] = []

        while True:
            start_idx = self._buffer.find(START_DELIMITER)
            if start_idx == -1:
                self._buffer = ""
                break

            # Remove garbage before start delimiter
            if start_idx > 0:
                self._buffer = self._buffer[start_idx:]

            end_idx = self._buffer.find(END_DELIMITER)
            if end_idx == -1:
                # Incomplete message, wait for more data
                break

            raw_message = self._buffer[: end_idx + len(END_DELIMITER)]
            self._buffer = self._buffer[end_idx + len(END_DELIMITER) :]

            try:
                message = self._parser.parse(raw_message)
                messages.append(message)
            except ParseError:
                # Skip malformed messages
                continue

        return messages

    @property
    def pending(self) -> str:
        """Return the current buffer of incomplete data."""
        return self._buffer

    def reset(self) -> None:
        """Clear the decoder buffer."""
        self._buffer = ""
