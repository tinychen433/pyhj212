"""Message model for HJ 212-2017 protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pyhj212.models.header import Header

if TYPE_CHECKING:
    from pyhj212.cp.models import CPField


@dataclass(frozen=True)
class Message:
    """Represents a complete HJ 212-2017 protocol message.

    Attributes:
        header: Message header containing routing and type info.
        data: Raw data payload string.
        cp: CP field content (command parameters).
        crc: CRC checksum value from the message.
        raw: Original raw message string for preservation.
    """

    header: Header
    data: str = ""
    cp: str = ""
    crc: str = ""
    raw: str = field(default="", repr=False, compare=False)

    @property
    def cp_fields(self) -> list[CPField]:
        """Parse the data payload into grouped CPField objects.

        Returns:
            List of CPField objects parsed from the data section.
        """
        from pyhj212.cp.parser import CPParser

        return CPParser().parse(self.data) if self.data else []
