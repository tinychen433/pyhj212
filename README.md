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

### 从 PyPI 安装

```bash
pip install pyhj212
```

项目地址：<https://pypi.org/project/pyhj212/>

### 从源码安装（开发模式）

```bash
git clone https://github.com/tinychen/pyhj212.git
cd pyhj212
uv sync --all-extras   # 或 pip install -e ".[dev]"
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
    mn="010000A8900016F000169DC0", flag="5",
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

CP 数据区由 `;` 分隔的键值对组成，`,` 分隔的逗号段属于同一监测因子的多个属性。

#### 扁平解析

```python
from pyhj212.cp.parser import CPParser

parser = CPParser()
fields = parser.parse("PNO=000000004;DataTime=20260902082000;a01001-Rtd=24.4")

for f in fields:
    print(f"{f.key} = {f.value}")
# PNO = 000000004
# DataTime = 20260902082000
# a01001-Rtd = 24.4
```

#### 归组解析

将同一监测因子（`tn0112`、`w01001` 等）的多个属性合并为一个父节点：

```python
cp = "DataTime=20261118134500;tn0112-Rtd=228.200,tn0112-Flag=N"
fields = parser.parse_grouped(cp)

for f in fields:
    if f.children:
        print(f"{f.key}:")
        for c in f.children:
            print(f"  {c.key} = {c.value}")
    else:
        print(f"{f.key} = {f.value}")
# DataTime = 20261118134500
# tn0112:
#   Rtd = 228.200
#   Flag = N
```

#### 序列化 JSON

```python
import json

data = [f.to_dict() for f in fields]
print(json.dumps(data, ensure_ascii=False, indent=2))
# [
#   {"DataTime": "20261118134500"},
#   {"tn0112": {"Rtd": "228.200", "Flag": "N"}}
# ]
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
