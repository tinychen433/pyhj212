"""High-level convenience functions for HJ 212-2017 protocol.

Mirrors the stdlib json.loads / json.dumps pattern: no class
instantiation required for common tasks.
"""

from __future__ import annotations

from pyhj212.cp.encoder import CPEncoder
from pyhj212.cp.models import CPField
from pyhj212.cp.parser import CPParser
from pyhj212.models.header import Header
from pyhj212.models.message import Message
from pyhj212.models.validation import ValidationResult
from pyhj212.protocol.encoder import Encoder
from pyhj212.protocol.parser import Parser
from pyhj212.protocol.validator import Validator

# Internal singletons (stateless classes, created once)
_parser = Parser()
_encoder = Encoder()
_validator = Validator()
_cp_parser = CPParser()
_cp_encoder = CPEncoder()


def parse(raw: str) -> Message:
    """Parse a raw HJ 212-2017 message string into a Message.

    The returned Message provides a ``cp_fields`` property that
    automatically parses the data section into grouped CPField objects.

    Args:
        raw: The complete raw message string (e.g. ``"##0084QN=...\\r\\n"``).

    Returns:
        A Message object with parsed header, data, and CRC.

    Raises:
        ParseError: If the message format is invalid.

    Example:
        >>> msg = parse("##0101QN=...;CP=&&RtdInterval=30&&1C80\\r\\n")
        >>> msg.header.cn
        '1062'
        >>> msg.cp_fields
        [CPField(key='RtdInterval', value='30')]
    """
    return _parser.parse(raw)


def encode(header: Header | dict[str, str], data: str | list[dict[str, object]]) -> str:
    """Encode a Header and data payload into a raw HJ 212-2017 string.

    Args:
        header: A Header object or a dict of header fields
                (e.g. ``{"CN": "1062", "PW": "123456"}``).
        data: The CP data payload — either a raw string or a list of dicts
              matching the ``to_dict()`` / ``from_dict()`` format, e.g.::

                  [{"DataTime": "20261118134500"},
                   {"tn0112": {"Rtd": "228.200", "Flag": "N"}}]

    Returns:
        The complete encoded message string.

    Raises:
        EncodeError: If the message cannot be encoded.

    Example:
        >>> raw = encode(
        ...     header={"CN": "1062", "PW": "100000", "MN": "ST0001"},
        ...     data=[{"RtdInterval": "30"}],
        ... )
    """
    if isinstance(header, dict):
        header = _dict_to_header(header)
    if isinstance(data, list):
        fields = [CPField.from_dict(d) for d in data]
        data = _cp_encoder.encode(fields)
    message = Message(header=header, data=data)
    return _encoder.encode(message)


def validate(raw: str) -> ValidationResult:
    """Validate a raw HJ 212-2017 message string.

    Checks delimiters, length field, CRC checksum, and required fields.

    Args:
        raw: The raw message string to validate.

    Returns:
        ValidationResult with is_valid, errors, and warnings.

    Example:
        >>> result = validate("##0101...\\r\\n")
        >>> if not result.is_valid:
        ...     print(result.errors)
    """
    return _validator.validate(raw)


def parse_cp(cp_string: str) -> list[CPField]:
    """Parse a CP (Command Parameter) field string into CPField objects.

    Handles both flat fields and grouped factor codes
    (e.g. ``tn0112-Rtd=228.200,tn0112-Flag=N``).

    Args:
        cp_string: The raw CP data section.

    Returns:
        List of CPField objects, with grouped factors as parents.

    Example:
        >>> fields = parse_cp("PNO=0001;DataTime=20260902082000")
        >>> fields[0].to_dict()
        {'PNO': '0001'}
    """
    return _cp_parser.parse(cp_string)


def encode_cp(fields: list[CPField]) -> str:
    """Encode CPField objects back into a CP field string.

    Args:
        fields: List of CPField objects.

    Returns:
        Semicolon-separated CP field string.

    Example:
        >>> raw = encode_cp([CPField(key="PNO", value="0001")])
        >>> raw
        'PNO=0001'
    """
    return _cp_encoder.encode(fields)


# -- Internal helpers --


def _dict_to_header(d: dict[str, str]) -> Header:
    """Convert a dict to a Header object.

    Accepts both lowercase keys (cn, pw, mn) and uppercase (CN, PW, MN).
    """
    norm: dict[str, str] = {}
    for k, v in d.items():
        norm[k.lower()] = v
    return Header(
        flag=norm.get("flag", ""),
        pno=norm.get("pno", ""),
        qn=norm.get("qn", ""),
        st=norm.get("st", ""),
        cn=norm.get("cn", ""),
        pw=norm.get("pw", ""),
        mn=norm.get("mn", ""),
    )
