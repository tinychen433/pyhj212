# API Reference

## Models

### `Header`

```python
@dataclass(frozen=True)
class Header:
    pn: str          # Pollutant number (station ID)
    cn: str          # Command number
    pw: str          # Password
    mn: str = ""     # Device number
    st: str = ""     # System type
    flag: int = 0    # Message flag
    pno: int = 0     # Packet number
    raw: str = ""    # Original header string
```

### `Message`

```python
@dataclass(frozen=True)
class Message:
    header: Header
    data: str = ""
    cp: str = ""
    crc: str = ""
    raw: str = ""
```

## Protocol

### `Parser`

```python
class Parser:
    def parse(self, raw: str) -> Message: ...
```

### `Encoder`

```python
class Encoder:
    def encode(self, message: Message) -> str: ...
```

### `Validator`

```python
class Validator:
    def validate(self, raw: str) -> ValidationResult: ...
    def validate_message(self, message: Message) -> ValidationResult: ...
```

### Checksum

```python
def calculate_crc(data: str) -> int: ...
def verify_crc(data: str, expected_crc: int) -> bool: ...
```

### Stream

```python
class StreamDecoder:
    def feed(self, data: bytes) -> list[Message]: ...
    @property
    def pending(self) -> str: ...
    def reset(self) -> None: ...
```

## CP (Command Parameters)

### `CPField`

```python
@dataclass(frozen=True)
class CPField:
    key: str
    value: str = ""
    children: list[CPField] = ...
    raw: str = ""
```

### `CPParser`

```python
class CPParser:
    def parse(self, cp_string: str) -> list[CPField]: ...
```

### `CPEncoder`

```python
class CPEncoder:
    def encode(self, fields: list[CPField]) -> str: ...
```

## Exceptions

| Exception | Description |
|-----------|-------------|
| `PyHJ212Error` | Base exception |
| `ParseError` | Parsing failure |
| `EncodeError` | Encoding failure |
| `ValidationError` | Validation failure |
| `ChecksumError` | CRC mismatch |
| `CPError` | CP field parsing failure |
