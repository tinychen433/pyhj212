# pyhj212

HJ 212-2017 协议核心协议的 Python 实现，提供消息编解码、CRC 校验、协议验证、TCP 流帧解码以及 CP 字段解析功能。

## 特性

| 功能 | 状态 |
|------|------|
| 消息解析 | ✅ |
| 消息编码 | ✅ |
| CRC-16 计算与校验 | ✅ |
| CP 字段解析与编码 | ✅ |
| 协议验证 | ✅ |
| TCP 流帧解码（粘包/分包） | ✅ |
| Dataclass 数据模型 | ✅ |

## 快速开始

### 安装

```bash
# 使用 uv 安装开发依赖
uv sync --all-extras

# 或直接安装
pip install -e .
```

### 解析消息

```python
from pyhj212.protocol.parser import Parser

raw = (
    "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
    "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
    "1C80\r\n"
)

parser = Parser()
msg = parser.parse(raw)

print(msg.header.cn)   # "1062"
print(msg.header.mn)   # "010000A8900016F000169DC0"
print(msg.data)        # "RtdInterval=30"
print(msg.crc)         # "1C80"
```

### 编码消息

```python
from pyhj212.models.header import Header
from pyhj212.models.message import Message
from pyhj212.protocol.encoder import Encoder

header = Header(
    qn="20160801085857223", st="32", cn="1062", pw="100000",
    mn="010000A8900016F000169DC0", flag=5, pno=0,
)
message = Message(header=header, data="RtdInterval=30")

encoder = Encoder()
raw = encoder.encode(message)
# "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;..."
```

### 验证消息

```python
from pyhj212.protocol.validator import Validator

validator = Validator()
result = validator.validate(raw)

if not result.is_valid:
    for error in result.errors:
        print(f"错误: {error}")
```

### TCP 流解码

```python
from pyhj212.protocol.stream import StreamDecoder

decoder = StreamDecoder()

# 分包场景
decoder.feed(b"##0030QN=...;F")
decoder.feed(b"lag=5;CP=&&RtdInterval=30&&1C80\r\n")

# 粘包场景
decoder.feed(b"##0030...&&1C80\r\n##0030...&&2A3B\r\n")
```

### CP 字段解析

```python
from pyhj212.cp.parser import CPParser

parser = CPParser()
fields = parser.parse("PNO=000000004;DataTime=20260902082000;a01001-Rtd=24.4")

for f in fields:
    print(f"{f.key} = {f.value}")
```

## 开发

参见 [DEVELOPMENT.md](DEVELOPMENT.md)。

```bash
# 运行测试
uv run pytest

# 代码检查
uv run ruff check src/pyhj212 tests
uv run ruff format src/pyhj212 tests
uv run mypy src/pyhj212
```

## 协议

- HJ 212-2017 《污染物在线监控（监测）系统数据传输标准》

## License

MIT
