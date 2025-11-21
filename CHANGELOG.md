# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with pyproject.toml, noxfile.py, and GitHub Actions workflows
- Core modules extracted from shotgrid-mcp-server:
  - `custom_types.py`: Type definitions for ShotGrid API
  - `models.py`: Pydantic models for filters and entities
  - `data_types.py`: Type conversion utilities
  - `filters.py`: FilterBuilder class with 20+ filter methods
- QueryBuilder class with chainable API:
  - Django-style filter syntax with __ operators (e.g., `field__contains`)
  - Support for `filter()`, `select()`, `order_by()`, `limit()`
  - Support for `execute()`, `first()`, `count()`, `exists()` methods
  - Query cloning and `to_dict()` conversion
- FieldMapper for resolving related field paths:
  - Automatic resolution of entity types from schema
  - Support for deep query format (field.EntityType.field)
  - Field resolution caching for performance
- Adapter pattern for different ShotGrid APIs:
  - BaseAdapter abstract interface
  - PythonAPIAdapter for shotgun_api3
  - Support for find, create, update, delete operations
- Comprehensive test suite with >90% coverage:
  - Tests for FilterBuilder and filter validation
  - Tests for QueryBuilder with mocks
  - Tests for filter processing and date handling
- Documentation:
  - README in English and Chinese
  - Quick start examples
  - API usage examples

## [0.1.0] - TBD

### Added
- First public release
- Basic query builder functionality
- Filter building and validation
- Type conversion utilities
- Support for shotgun_api3 integration

