"""CRC-16 calculation for HJ 212-2017 protocol."""

from __future__ import annotations

from pyhj212.constants import CRC_INITIAL, CRC_POLYNOMIAL


def calculate_crc(data: str) -> int:
    """Calculate CRC-16 checksum for HJ 212-2017 message data.

    Algorithm: reflected CRC-16 with polynomial 0xA001, initial value
    0xFFFF, and per-byte high-byte folding (crc >> 8) ^ byte.

    Args:
        data: The message data string to calculate CRC for.

    Returns:
        The CRC-16 value as an integer.
    """
    crc = CRC_INITIAL
    for byte in data.encode("ascii"):
        crc = (crc >> 8) ^ byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ CRC_POLYNOMIAL
            else:
                crc >>= 1
    return crc & 0xFFFF


def verify_crc(data: str, expected_crc: int) -> bool:
    """Verify CRC-16 checksum against expected value.

    Args:
        data: The message data string.
        expected_crc: The expected CRC value to verify against.

    Returns:
        True if the calculated CRC matches the expected value.
    """
    return calculate_crc(data) == expected_crc
