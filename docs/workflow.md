# 开发工作流与版本管理

## 版本规则

遵循语义化版本 `MAJOR.MINOR.PATCH`（如 `0.1.0`）：

| 类型 | 场景 | 示例 |
|------|------|------|
| **PATCH** | 修复 bug、文档、测试 | `0.1.0` → `0.1.1` |
| **MINOR** | 新增功能（向后兼容） | `0.1.1` → `0.2.0` |
| **MAJOR** | 破坏性 API 变更 | `0.2.0` → `1.0.0` |

版本号定义在 `pyproject.toml`：

```toml
[project]
version = "0.1.0"
```

## 日常开发

每次提交遵循 Conventional Commits：

```
<type>(<scope>): <subject>

<body — 说明"为什么"做这次修改>
```

| type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 文档 |
| `refactor` | 重构（无功能变化） |
| `test` | 测试 |
| `chore` | 构建/工具链 |

### 开发检查清单

每完成一个功能点：

```bash
# 1. 跑测试
uv run pytest

# 2. lint + format
uv run ruff check src/pyhj212 tests
uv run ruff format src/pyhj212 tests

# 3. 类型检查
uv run mypy src/pyhj212

# 4. 提交
git add .
git commit -m "feat(parser): add grouped CP parsing"
git push origin main
```

## 发布流程

### 1. 确认版本号

根据本次发布的变更类型，更新 `pyproject.toml` 中的版本号：

```diff
- version = "0.1.0"
+ version = "0.1.1"
```

### 2. 跑完整检查

```bash
uv run pytest
uv run ruff check src/pyhj212 tests
uv run ruff format --check src/pyhj212 tests
uv run mypy src/pyhj212
```

### 3. 提交并打 tag

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main --tags
```

### 4. 构建

```bash
uv build
```

产物在 `dist/` 目录：
- `dist/pyhj212-0.1.1.tar.gz` — 源码包
- `dist/pyhj212-0.1.1-py3-none-any.whl` — wheel 包

### 5. 发布到 PyPI

```bash
# 首次需要配置 token
uvx twine upload dist/*

# 或使用 uv 原生发布（uv 1.0+）
uv publish
```

发布前建议先用 `--repository testpypi` 测试：

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

### 6. 验证

```bash
# 安装刚发布的版本
pip install pyhj212==0.1.1 --force-reinstall

# 确认版本
python -c "import pyhj212; print(pyhj212.__version__)"
```

## 分支策略

单分支 `main` + tag 发布：

```
main ──●──●──●── v0.1.0
               ├──●──●── v0.1.1
                       ├──●── feat/xxx (临时功能分支)
                       └──●── v0.2.0
```

- **main**：始终可发布，所有提交合入主分支
- **临时分支**：功能复杂时可 `feat/xxx` 分支，完成后合并回 main
- **tag**：每次发布打一个 `vX.Y.Z` tag

## 快速参考

| 操作 | 命令 |
|------|------|
| 升级 PATCH | `version = "0.1.0"` → `"0.1.1"` |
| 升级 MINOR | `version = "0.1.0"` → `"0.2.0"` |
| 升级 MAJOR | `version = "0.1.0"` → `"1.0.0"` |
| 打 tag | `git tag -a v0.1.0 -m "Release v0.1.0"` |
| 构建 | `uv build` |
| 发布 | `uv publish` |
| 验证安装 | `pip install pyhj212==X.Y.Z --force-reinstall` |
