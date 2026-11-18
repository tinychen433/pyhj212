"""Example: Encode an HJ 212-2017 message."""

from pyhj212.models.header import Header
from pyhj212.models.message import Message
from pyhj212.protocol.encoder import Encoder


def main() -> None:
    """Demonstrate encoding a Message to a raw HJ 212-2017 string."""
    header = Header(
        cn="1062",
        pw="100000",
        mn="010000A8900016F000169DC0",
        st="32",
        flag=5,
        qn="20160801085857223",
    )

    message = Message(
        header=header,
        data="RtdInterval=30",
    )

    encoder = Encoder()
    raw = encoder.encode(message)

    print(f"Encoded message:\n{raw}")


if __name__ == "__main__":
    main()
