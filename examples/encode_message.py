"""Example: Encode an HJ 212-2017 message."""

from pyhj212.models.header import Header
from pyhj212.models.message import Message
from pyhj212.protocol.encoder import Encoder


def main() -> None:
    """Demonstrate encoding a Message to a raw HJ 212-2017 string."""
    header = Header(
        pn="21",
        cn="2011",
        pw="123456",
        mn="ST0001",
        st="32",
        flag=4,
        pno=1,
    )

    message = Message(
        header=header,
        data="w01001-Rtd=12.5;w01002-Rtd=34.0",
    )

    encoder = Encoder()
    raw = encoder.encode(message)

    print(f"Encoded message:\n{raw}")


if __name__ == "__main__":
    main()
