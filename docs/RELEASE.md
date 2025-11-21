# Release Process

## Automatic Release (Recommended)

The project uses an automated release workflow that triggers when code is merged to the `main` branch.

### How it works:

1. **Update version** in `pyproject.toml`
2. **Merge to main** branch
3. **Auto-tag workflow** runs automatically:
   - Reads version from `pyproject.toml`
   - Creates a git tag (e.g., `v0.1.0`)
   - Pushes the tag to GitHub
4. **Publish workflow** triggers automatically when tag is created:
   - Runs tests (lint, pytest, mypy)
   - Builds distribution packages
   - Publishes to PyPI
   - Creates GitHub Release with changelog

### Steps to release a new version:

1. Update the version in `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"  # Update this
   ```

2. Commit and push to a feature branch:
   ```bash
   git add pyproject.toml
   git commit -m "chore: bump version to 0.2.0"
   git push origin feature/version-bump
   ```

3. Create a Pull Request and merge to `main`

4. The auto-tag workflow will:
   - Detect the new version
   - Create tag `v0.2.0`
   - Trigger the publish workflow

5. Monitor the workflow at: https://github.com/loonghao/shotgrid-query/actions

## Manual Release

If you need to manually trigger a release:

### Option 1: Create tag manually

```bash
# Update version in pyproject.toml first
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0"
git push origin main

# Create and push tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### Option 2: Use GitHub Actions UI

1. Go to [Actions](https://github.com/loonghao/shotgrid-query/actions)
2. Select "Publish to PyPI" workflow
3. Click "Run workflow"
4. Select branch and options
5. Click "Run workflow" button

## Prerequisites

### PyPI Configuration

The publish workflow uses **Trusted Publishers** (OIDC) for secure authentication with PyPI.

#### Setup Trusted Publisher on PyPI:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher with:
   - **PyPI Project Name**: `shotgrid-query`
   - **Owner**: `loonghao`
   - **Repository name**: `shotgrid-query`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`

This eliminates the need for API tokens and provides better security.

### GitHub Environment

The workflow uses a GitHub environment named `pypi`:

1. Go to repository Settings → Environments
2. Create environment named `pypi`
3. (Optional) Add protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches (only `main`)

## Troubleshooting

### Tag already exists

If the auto-tag workflow detects an existing tag, it will skip tag creation. To fix:

1. Update version in `pyproject.toml` to a new version
2. Commit and merge to main

### Publish workflow not triggered

Check:
1. Tag format is correct (`v*` pattern, e.g., `v0.1.0`)
2. Tag was pushed to GitHub: `git ls-remote --tags origin`
3. Workflow file is in the main branch

### PyPI publish fails

Common issues:
1. **Version already exists on PyPI**: Update version in `pyproject.toml`
2. **Trusted Publisher not configured**: Follow setup steps above
3. **Package name conflict**: Ensure package name is available on PyPI

### Tests fail during publish

The publish workflow runs tests before publishing. If tests fail:

1. Fix the issues locally
2. Push fixes to main
3. Update version (if needed)
4. The workflow will run again

You can also manually trigger with `skip-tests: true` option (not recommended for production).

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): Add functionality (backwards compatible)
- **PATCH** version (0.0.1): Bug fixes (backwards compatible)

Examples:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.0` → `0.2.0`: New feature
- `0.9.0` → `1.0.0`: First stable release

## Changelog

The GitHub Release is automatically generated with:
- Commit messages grouped by type (feat, fix, refactor, etc.)
- Comparison link to previous release
- Distribution artifacts attached

To improve changelog quality, use conventional commits:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `chore: update dependencies`

