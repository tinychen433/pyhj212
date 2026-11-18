"""Message header model for HJ 212-2017 protocol."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Header:
    """Represents the header section of an HJ 212-2017 message.

    The header contains metadata about the message including the
    protocol version, message type, and routing information.

    Attributes:
        qn: Request number (请求编号), 17-char timestamp format.
        st: System type, identifies the equipment category.
        cn: Command number, identifies the message type.
        pw: Password for authentication, typically 6 characters.
        mn: Device number (monitoring station), typically 24 characters.
        flag: Message flag indicating encryption and packaging.
        pno: Packet number for multi-part messages.
    """

    qn: str = ""
    st: str = ""
    cn: str = ""
    pw: str = ""
    mn: str = ""
    flag: int = 0
    pno: int = 0

    raw: str = field(default="", repr=False, compare=False)

    def to_string(self) -> str:
        """Serialize the header to HJ 212-2017 format.

        Returns:
            The formatted header string.
        """
        parts = []
        if self.qn:
            parts.append(f"QN={self.qn}")
        if self.st:
            parts.append(f"ST={self.st}")
        if self.cn:
            parts.append(f"CN={self.cn}")
        if self.pw:
            parts.append(f"PW={self.pw}")
        if self.mn:
            parts.append(f"MN={self.mn}")
        parts.append(f"Flag={self.flag}")
        parts.append(f"PNO={self.pno}")
        return ";".join(parts)
