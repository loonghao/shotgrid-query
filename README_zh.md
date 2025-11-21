# ShotGrid Query Builder

[![PyPI version](https://badge.fury.io/py/shotgrid-query.svg)](https://badge.fury.io/py/shotgrid-query)
[![Python Versions](https://img.shields.io/pypi/pyversions/shotgrid-query.svg)](https://pypi.org/project/shotgrid-query/)
[![Downloads](https://static.pepy.tech/badge/shotgrid-query)](https://pepy.tech/project/shotgrid-query)
[![Downloads/Month](https://static.pepy.tech/badge/shotgrid-query/month)](https://pepy.tech/project/shotgrid-query)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/loonghao/shotgrid-query/workflows/Tests/badge.svg)](https://github.com/loonghao/shotgrid-query/actions)
[![codecov](https://codecov.io/gh/loonghao/shotgrid-query/branch/main/graph/badge.svg)](https://codecov.io/gh/loonghao/shotgrid-query)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://github.com/python/mypy)
[![GitHub stars](https://img.shields.io/github/stars/loonghao/shotgrid-query.svg?style=social&label=Star)](https://github.com/loonghao/shotgrid-query)
[![GitHub forks](https://img.shields.io/github/forks/loonghao/shotgrid-query.svg?style=social&label=Fork)](https://github.com/loonghao/shotgrid-query/fork)

一个为 ShotGrid/Flow Production Tracking API 设计的 Pythonic 查询构建器和 ORM 风格的抽象层。

[English Documentation](README.md)

## 🎯 特性

- **Pythonic API**: 链式调用的查询构建器,方法名直观易懂
- **类型安全**: 完整的类型提示和 Pydantic 验证
- **灵活**: 同时支持 `shotgun_api3` 和原始过滤器字典
- **强大**: 支持复杂过滤器、关联字段和基于时间的查询
- **轻量级**: 最小化依赖,可独立使用
- **经过充分测试**: 全面的测试套件,覆盖率 >90%

## 📦 安装

```bash
# 基础安装
pip install shotgrid-query

# 包含 ShotGrid API 支持
pip install shotgrid-query[shotgrid]

# 开发环境
pip install shotgrid-query[dev]
```

## 🚀 快速开始

### 传统 ShotGrid API (之前)

```python
import shotgun_api3

sg = shotgun_api3.Shotgun(url, script_name, api_key)

# 复杂的过滤器语法
filters = [
    ["sg_status_list", "is", "ip"],
    ["project", "is", {"type": "Project", "id": 123}],
    ["created_at", "in_last", [7, "DAY"]]
]
fields = ["code", "description", "project.Project.name"]
result = sg.find("Shot", filters, fields)
```

### 使用 shotgrid-query (之后)

```python
from shotgrid_query import Query

# 链式调用,可读性强的查询构建器
query = (
    Query("Shot")
    .filter(sg_status_list="ip")
    .filter(project_id=123)
    .filter(created_at__in_last="7 days")
    .select("code", "description")
    .select_related("project", fields=["name"])
    .order_by("-created_at")
    .limit(100)
)

# 使用 shotgun_api3 连接执行
result = query.execute(sg)

# 或获取原始过滤器/字段用于手动使用
filters = query.to_filters()  # 返回元组列表
fields = query.to_fields()    # 返回字段名列表
```

## 🔍 Schema 验证

在执行查询前验证 ShotGrid schema,及早发现错误:

```python
from shotgrid_query import Query

# 开发模式 - 每次操作自动验证
query = Query("Shot", sg=sg, auto_validate=True)
query.filter(code="SHOT_010").select("code", "description")

# 自动验证,如果无效会抛出 ValueError
result = query.execute(sg)
```

### 手动验证

```python
# 使用 schema 创建查询
schema = sg.schema_field_read("Shot")
query = Query("Shot", schema=schema)
query.filter(code="SHOT_010").select("invalid_field")

# 手动验证
errors = query.validate()
if errors:
    for error in errors:
        print(f"❌ {error.field}: {error.message}")
        if error.suggestion:
            print(f"💡 {error.suggestion}")
else:
    result = query.execute(sg)
```

### 按需验证

```python
# 转换为 filters/fields 时验证
try:
    filters = query.to_filters(verify=True)
    fields = query.to_fields(verify=True)
except ValueError as e:
    print(f"验证失败:\n{e}")
```

### 详细的错误提示

验证失败时,会得到有用的错误信息:

```python
# 字段不存在
❌ invalid_field: Field does not exist in Shot
💡 Available fields: code, description, id, project, sg_status_list (and 45 more)

# 操作符与字段类型不兼容
❌ code: Operator 'greater_than' is not valid for field type 'text'
💡 Valid operators for text fields: contains, ends_with, in, is, is_not, not_contains, not_in, starts_with

# 值类型不匹配
❌ id: Value must be a number, got str
💡 Example: query.filter(id=123)
```

### Schema 缓存

Schema 会自动缓存以避免重复的 API 调用:

```python
from shotgrid_query import SchemaCache

# 设置自定义 TTL (默认: 1 小时)
SchemaCache.set_ttl(3600)

# 需要时清除缓存
SchemaCache.clear()
```

## 📚 文档

- [快速开始指南](docs/quickstart.md)
- [API 参考](docs/api_reference.md)
- [示例](docs/examples.md)

## 🤝 贡献

欢迎贡献!请随时提交 Pull Request。

### 开发环境设置

1. 克隆仓库:
```bash
git clone https://github.com/loonghao/shotgrid-query.git
cd shotgrid-query
```

2. 安装依赖:
```bash
pip install -e ".[dev]"
```

3. 安装 pre-commit 钩子:
```bash
pre-commit install
```

这将在每次提交前自动运行代码格式化和 lint 检查。

### 运行测试

```bash
# 运行所有测试
pytest

# 运行并显示覆盖率
pytest --cov=src/shotgrid_query --cov-report=term-missing

# 运行特定测试文件
pytest tests/test_query.py -v
```

### 代码质量

```bash
# 格式化代码
ruff format src tests

# Lint 检查
ruff check src tests

# 类型检查
mypy src/shotgrid_query
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

本库从 [shotgrid-mcp-server](https://github.com/loonghao/shotgrid-mcp-server) 中提取,
旨在为 ShotGrid 社区提供一个可复用的查询构建器。

