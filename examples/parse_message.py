"""Example: Parse an HJ 212-2017 message."""

from pyhj212 import parse


def main() -> None:
    """Demonstrate message parsing with automatic CP field extraction."""
    raw = (
        "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
        "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
        "1C80\r\n"
    )

    msg = parse(raw)

    print(f"CN: {msg.header.cn}")
    print(f"MN: {msg.header.mn}")
    print(f"Data: {msg.data}")
    print(f"CRC: {msg.crc}")
    print()

    # CP fields are auto-parsed
    for f in msg.cp_fields:
        print(f.to_dict())


if __name__ == "__main__":
    main()
