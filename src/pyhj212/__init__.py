# PyHJ212 - HJ 212-2017 Protocol Library

"""A Python library for HJ212 protocol encoding, decoding, validation, and communication.

Top-level convenience functions (zero-instantiation API)::

    from pyhj212 import parse, encode, validate, parse_cp, encode_cp

    msg = parse(raw)           # -> Message
    raw = encode(header, data) # -> str
    result = validate(raw)     # -> ValidationResult
    fields = parse_cp(cp_str)  # -> list[CPField]
"""

from __future__ import annotations

# High-level convenience functions
from pyhj212.api import encode, encode_cp, parse, parse_cp, validate
from pyhj212.cp import CPEncoder, CPParser

# Core models
from pyhj212.cp.models import CPField

# Exceptions
from pyhj212.exceptions import (
    ChecksumError,
    CPError,
    EncodeError,
    ParseError,
    PyHJ212Error,
    ValidationError,
)
from pyhj212.models.header import Header
from pyhj212.models.message import Message
from pyhj212.models.validation import ValidationResult

# Advanced classes (backward compatibility)
from pyhj212.protocol import Encoder, Parser, StreamDecoder, Validator

# CRC utilities
from pyhj212.protocol.checksum import calculate_crc, verify_crc

# Version
from pyhj212.version import __version__, __version_tuple__

__all__ = [
    # Convenience functions (primary API)
    "parse",
    "encode",
    "validate",
    "parse_cp",
    "encode_cp",
    # Models
    "Header",
    "Message",
    "CPField",
    "ValidationResult",
    # CRC utilities
    "calculate_crc",
    "verify_crc",
    # Advanced classes
    "Parser",
    "Encoder",
    "Validator",
    "StreamDecoder",
    "CPParser",
    "CPEncoder",
    # Exceptions
    "PyHJ212Error",
    "ParseError",
    "EncodeError",
    "ValidationError",
    "ChecksumError",
    "CPError",
    # Version
    "__version__",
    "__version_tuple__",
]
