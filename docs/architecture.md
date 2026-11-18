# Architecture

## Design Principles

1. **Protocol Independence**: Core protocol logic is decoupled from network transport. The parser, encoder, and validator operate on strings, not sockets.

2. **Data Preservation**: Raw message data is preserved alongside parsed structures. Unknown fields are not silently discarded.

3. **Explicit Errors**: Parsing and validation failures raise descriptive exceptions. No silent error swallowing.

## Module Layout

```
pyhj212/
├── models/       # Data classes for messages, headers, validation results
├── protocol/     # Parsing, encoding, validation, CRC, stream decoding
├── cp/           # CP (Command Parameter) field handling
├── constants.py  # Protocol constants (delimiters, CRC config)
└── exceptions.py # Custom exception hierarchy
```

## Message Flow

```
Raw String ──► Parser ──► Message (dataclass)
                  │
                  └──► Validator ──► ValidationResult

Message (dataclass) ──► Encoder ──► Raw String
```

## CRC Implementation

HJ 212-2017 uses CRC-16 with:
- Polynomial: 0xA001
- Initial value: 0xFFFF
- Output: 4-character uppercase hex string

## TCP Stream Decoding

The `StreamDecoder` handles:
- **Fragmentation**: Partial messages across multiple reads
- **Concatenation**: Multiple messages in a single buffer
- **Recovery**: Graceful handling of malformed data
