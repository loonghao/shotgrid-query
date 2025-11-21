# ShotGrid Query Builder

[![PyPI version](https://badge.fury.io/py/shotgrid-query.svg)](https://badge.fury.io/py/shotgrid-query)
[![Python Versions](https://img.shields.io/pypi/pyversions/shotgrid-query.svg)](https://pypi.org/project/shotgrid-query/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/loonghao/shotgrid-query/workflows/Tests/badge.svg)](https://github.com/loonghao/shotgrid-query/actions)
[![Coverage](https://codecov.io/gh/loonghao/shotgrid-query/branch/main/graph/badge.svg)](https://codecov.io/gh/loonghao/shotgrid-query)

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

## 📚 文档

- [快速开始指南](docs/quickstart.md)
- [API 参考](docs/api_reference.md)
- [示例](docs/examples.md)

## 🤝 贡献

欢迎贡献!请随时提交 Pull Request。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

本库从 [shotgrid-mcp-server](https://github.com/loonghao/shotgrid-mcp-server) 中提取,
旨在为 ShotGrid 社区提供一个可复用的查询构建器。

