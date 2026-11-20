"""Example: Encode an HJ 212-2017 message."""

from pyhj212 import Header, encode


def main() -> None:
    """Demonstrate encoding a message to a raw HJ 212-2017 string."""
    # Method 1: Header object
    header = Header(
        cn="1062",
        pw="100000",
        mn="010000A8900016F000169DC0",
        st="32",
        flag="5",
        qn="20160801085857223",
    )
    raw = encode(header, [{"RtdInterval": "30"}])
    print(f"Encoded message:\n{raw}")
    raw = encode(
        header, [{"DataTime": "20261118134500"}, {"tn0112": {"Rtd": "228.200", "Flag": "N"}}]
    )

    # Method 2: dict shortcut
    # raw = encode(
    #     header={"CN": "1062", "PW": "100000", "MN": "010000A8900016F000169DC0"},
    #     data="RtdInterval=30",
    # )

    print(f"Encoded message:\n{raw}")


if __name__ == "__main__":
    main()
