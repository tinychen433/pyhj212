# pyhj212

HJ 212-2017 协议核心协议的 Python 实现，提供消息编解码、CRC 校验、协议验证以及 CP 字段解析功能。

## 特性

| 功能 | 状态 |
|------|------|
| 消息解析 | ✅ |
| 消息编码 | ✅ |
| CRC-16 计算与校验 | ✅ |
| CP 字段解析与编码 | ✅ |
| 协议验证 | ✅ |
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
from pyhj212 import parse

raw = (
    "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;"
    "MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&"
    "1C80\r\n"
)

msg = parse(raw)

print(msg.header.cn)   # "1062"
print(msg.header.mn)   # "010000A8900016F000169DC0"
print(msg.data)        # "RtdInterval=30"
print(msg.crc)         # "1C80"

# 自动解析 CP 字段
for f in msg.cp_fields:
    print(f.to_dict())
# {"RtdInterval": "30"}
```

### 编码消息

```python
from pyhj212 import encode, Header

# 字符串 data
header = Header(
    qn="20160801085857223", st="32", cn="1062", pw="100000",
    mn="010000A8900016F000169DC0", flag="5",
)
raw = encode(header, "RtdInterval=30")

# list[dict] data（推荐）
raw = encode(
    header={"CN": "1062", "PW": "100000", "MN": "ST0001"},
    data=[
        {"DataTime": "20261118134500"},
        {"tn0112": {"Rtd": "228.200", "Flag": "N"}},
    ],
)
```

### 验证消息

```python
from pyhj212 import validate

result = validate(raw)

if not result.is_valid:
    for error in result.errors:
        print(f"错误: {error}")
```

### CP 字段解析

CP 数据区由 `;` 分隔的键值对组成，`,` 分隔的逗号段属于同一监测因子的多个属性。

```python
from pyhj212 import parse_cp, encode_cp

# 解析
fields = parse_cp("DataTime=20261118134500;tn0112-Rtd=228.200,tn0112-Flag=N")

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

# 编码
raw = encode_cp(fields)

# JSON 序列化
import json
print(json.dumps([f.to_dict() for f in fields], ensure_ascii=False, indent=2))
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
