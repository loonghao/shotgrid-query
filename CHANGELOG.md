# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### Added
- First public release
- Basic query builder functionality
- Filter building and validation
- Type conversion utilities
- Support for shotgun_api3 integration

## v0.2.1 (2025-11-21)

### Fix

- **ci**: ensure PAT_TOKEN is used consistently in bump-version workflow
- **ci**: ensure bump-version workflow triggers publish workflow

## v0.2.0 (2025-11-21)

### Feat

- add schema validation with detailed error messages
- implement QueryBuilder, FieldMapper, and adapters
- initial project setup and core module extraction

### Fix

- require Python 3.10+ for union type syntax
- resolve all mypy type errors and ruff lint issues
