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

## 🔍 Schema Validation

Validate your queries against ShotGrid schema before execution to catch errors early:

```python
from shotgrid_query import Query

# Development mode - auto-validate on every operation
query = Query("Shot", sg=sg, auto_validate=True)
query.filter(code="SHOT_010").select("code", "description")

# Validation happens automatically, raises ValueError if invalid
result = query.execute(sg)
```

### Manual Validation

```python
# Create query with schema
schema = sg.schema_field_read("Shot")
query = Query("Shot", schema=schema)
query.filter(code="SHOT_010").select("invalid_field")

# Manually validate
errors = query.validate()
if errors:
    for error in errors:
        print(f"❌ {error.field}: {error.message}")
        if error.suggestion:
            print(f"💡 {error.suggestion}")
else:
    result = query.execute(sg)
```

### Validation on Demand

```python
# Validate when converting to filters/fields
try:
    filters = query.to_filters(verify=True)
    fields = query.to_fields(verify=True)
except ValueError as e:
    print(f"Validation failed:\n{e}")
```

### Detailed Error Messages

When validation fails, you get helpful error messages:

```python
# Field doesn't exist
❌ invalid_field: Field does not exist in Shot
💡 Available fields: code, description, id, project, sg_status_list (and 45 more)

# Operator not compatible with field type
❌ code: Operator 'greater_than' is not valid for field type 'text'
💡 Valid operators for text fields: contains, ends_with, in, is, is_not, not_contains, not_in, starts_with

# Value type mismatch
❌ id: Value must be a number, got str
💡 Example: query.filter(id=123)
```

### Schema Caching

Schema is automatically cached to avoid repeated API calls:

```python
from shotgrid_query import SchemaCache

# Set custom TTL (default: 1 hour)
SchemaCache.set_ttl(3600)

# Clear cache if needed
SchemaCache.clear()
```

## 📚 Documentation

- [Quick Start Guide](docs/quickstart.md)
- [API Reference](docs/api_reference.md)
- [Examples](docs/examples.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/loonghao/shotgrid-query.git
cd shotgrid-query
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

This will automatically run code formatting and linting checks before each commit.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/shotgrid_query --cov-report=term-missing

# Run specific test file
pytest tests/test_query.py -v
```

### Code Quality

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type check
mypy src/shotgrid_query
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This library was extracted from [shotgrid-mcp-server](https://github.com/loonghao/shotgrid-mcp-server) to provide
a reusable query builder for the ShotGrid community.

