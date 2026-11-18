# Examples

## Parsing a Message

```python
from pyhj212.protocol.parser import Parser

raw = (
    "##0084PN=21;CN=2011;PW=123456;MN=ST0001;ST=32;Flag=4;PNO=1"
    "&&w01001-Rtd=12.5;w01002-Rtd=34.0"
    "1A2B\r\n"
)

parser = Parser()
message = parser.parse(raw)

print(message.header.cn)  # "2011"
print(message.data)       # "w01001-Rtd=12.5;w01002-Rtd=34.0"
```

## Encoding a Message

```python
from pyhj212.models.header import Header
from pyhj212.models.message import Message
from pyhj212.protocol.encoder import Encoder

header = Header(
    pn="21", cn="2011", pw="123456",
    mn="ST0001", st="32", flag=4, pno=1,
)

message = Message(
    header=header,
    data="w01001-Rtd=12.5;w01002-Rtd=34.0",
)

encoder = Encoder()
raw = encoder.encode(message)
```

## Validating a Message

```python
from pyhj212.protocol.validator import Validator

validator = Validator()
result = validator.validate(raw)

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

## Stream Decoding

```python
from pyhj212.protocol.stream import StreamDecoder

decoder = StreamDecoder()

# Fragmented message across two reads
decoder.feed(b"##0030PN=21;CN=2011;PW=123456;MN=ST0001;ST=32;F")
decoder.feed(b"lag=4;PNO=1&&w01001-Rtd=12.5\r\n")
```

## CP Field Parsing

```python
from pyhj212.cp.parser import CPParser

parser = CPParser()
fields = parser.parse("w01001-Rtd=12.5;w01002-Rtd=34.0")

for field in fields:
    print(f"{field.key} = {field.value}")
```
