"""Example: Decode HJ 212-2017 messages from a TCP stream."""

from pyhj212.protocol.stream import StreamDecoder


def main() -> None:
    """Demonstrate decoding fragmented TCP stream data."""
    decoder = StreamDecoder()

    # Simulate fragmented stream: first message split across two reads
    chunk1 = b"##0030PN=21;CN=2011;PW=123456;MN=ST0001;ST=32;F"
    chunk2 = b"lag=4;PNO=1&&w01001-Rtd=12.5\r\n"

    # Simulate concatenated messages: two messages in one read
    chunk3 = b"##0030PN=21;CN=2011;PW=123456;MN=ST0001;ST=32;Flag=4;PNO=1&&w01001-Rtd=12.5\r\n##0030PN=21;CN=2011;PW=123456;MN=ST0001;ST=32;Flag=4;PNO=2&&w01002-Rtd=34.0\r\n"

    print("=== Fragmented messages ===")
    messages = decoder.feed(chunk1)
    print(f"  Chunk 1: {len(messages)} message(s)")

    messages = decoder.feed(chunk2)
    print(f"  Chunk 2: {len(messages)} message(s)")

    print(f"\nPending buffer: {decoder.pending!r}")

    print("\n=== Concatenated messages ===")
    messages = decoder.feed(chunk3)
    print(f"  Chunk 3: {len(messages)} message(s)")

    for i, msg in enumerate(messages):
        print(f"  Message {i + 1}: {msg.header.cn}")


if __name__ == "__main__":
    main()
