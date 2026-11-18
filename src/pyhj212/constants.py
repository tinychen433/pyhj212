"""Protocol constants for HJ 212-2017."""

from __future__ import annotations

# Message delimiters
START_DELIMITER = "##"
END_DELIMITER = "\r\n"

# CRC configuration
CRC_POLYNOMIAL = 0xA001
CRC_INITIAL = 0xFFFF

# Message length limits
MAX_DATA_LENGTH = 9999
MIN_DATA_LENGTH = 0

# CP command types
CP_CMD_READ = "READ"
CP_CMD_WRITE = "WRITE"
CP_CMD_ACK = "ACK"
CP_CMD_NACK = "NACK"

# Message types
MSG_TYPE_REQUEST = "REQUEST"
MSG_TYPE_RESPONSE = "RESPONSE"
