## Description
<!-- Describe your changes in detail -->

## Type of Change
<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement
- [ ] CI/CD changes
- [ ] Dependency updates

## Version Update
<!-- If this PR should trigger a release, update the version -->

- [ ] Version updated in `pyproject.toml`
  - Current version: `0.1.0`
  - New version: `_._._`
  - Follows [Semantic Versioning](https://semver.org/)

**Note**: When merged to `main`, if version is updated, a new release will be automatically created and published to PyPI.

## Checklist
<!-- Mark completed items with an "x" -->

- [ ] My code follows the code style of this project (ruff)
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] All new and existing tests pass locally
- [ ] I have updated the documentation accordingly
- [ ] I have added type hints and they pass mypy check
- [ ] My changes generate no new warnings

## Testing
<!-- Describe the tests you ran to verify your changes -->

```bash
# Example commands
ruff check src tests
pytest --cov=src/shotgrid_query
mypy src/shotgrid_query
```

## Related Issues
<!-- Link to related issues -->

Closes #
Related to #

## Additional Notes
<!-- Any additional information that reviewers should know -->

