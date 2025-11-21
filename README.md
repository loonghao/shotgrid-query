# ShotGrid Query Builder

[![PyPI version](https://badge.fury.io/py/shotgrid-query.svg)](https://badge.fury.io/py/shotgrid-query)
[![Python Versions](https://img.shields.io/pypi/pyversions/shotgrid-query.svg)](https://pypi.org/project/shotgrid-query/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/loonghao/shotgrid-query/workflows/Tests/badge.svg)](https://github.com/loonghao/shotgrid-query/actions)
[![Coverage](https://codecov.io/gh/loonghao/shotgrid-query/branch/main/graph/badge.svg)](https://codecov.io/gh/loonghao/shotgrid-query)

A Pythonic query builder and ORM-like abstraction layer for ShotGrid/Flow Production Tracking API.

[中文文档](README_zh.md)

## 🎯 Features

- **Pythonic API**: Chainable query builder with intuitive method names
- **Type Safety**: Full type hints and Pydantic validation
- **Flexible**: Works with both `shotgun_api3` and raw filter dictionaries
- **Powerful**: Support for complex filters, related fields, and time-based queries
- **Lightweight**: Minimal dependencies, can be used independently
- **Well-tested**: Comprehensive test suite with >90% coverage

## 📦 Installation

```bash
# Basic installation
pip install shotgrid-query

# With ShotGrid API support
pip install shotgrid-query[shotgrid]

# For development
pip install shotgrid-query[dev]
```

## 🚀 Quick Start

### Traditional ShotGrid API (Before)

```python
import shotgun_api3

sg = shotgun_api3.Shotgun(url, script_name, api_key)

# Complex filter syntax
filters = [
    ["sg_status_list", "is", "ip"],
    ["project", "is", {"type": "Project", "id": 123}],
    ["created_at", "in_last", [7, "DAY"]]
]
fields = ["code", "description", "project.Project.name"]
result = sg.find("Shot", filters, fields)
```

### With shotgrid-query (After)

```python
from shotgrid_query import Query

# Chainable, readable query builder
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

# Execute with shotgun_api3 connection
result = query.execute(sg)

# Or get raw filters/fields for manual use
filters = query.to_filters()  # Returns list of tuples
fields = query.to_fields()    # Returns list of field names
```

## 📚 Documentation

- [Quick Start Guide](docs/quickstart.md)
- [API Reference](docs/api_reference.md)
- [Examples](docs/examples.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This library was extracted from [shotgrid-mcp-server](https://github.com/loonghao/shotgrid-mcp-server) to provide
a reusable query builder for the ShotGrid community.

