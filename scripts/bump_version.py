#!/usr/bin/env python3
"""Script to bump version in pyproject.toml."""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_current_version(pyproject_path: Path) -> str:
    """Get current version from pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def update_version(pyproject_path: Path, new_version: str) -> None:
    """Update version in pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")
    updated = re.sub(
        r'(version\s*=\s*)"[^"]+"',
        rf'\1"{new_version}"',
        content,
    )
    pyproject_path.write_text(updated, encoding="utf-8")


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse semantic version string."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)."""
    major, minor, patch = parse_version(current)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def check_git_status() -> bool:
    """Check if git working directory is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        return False


def check_tag_exists(tag: str) -> bool:
    """Check if git tag already exists."""
    try:
        subprocess.run(
            ["git", "rev-parse", tag],
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bump version in pyproject.toml")
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump",
    )
    parser.add_argument(
        "--version",
        help="Specific version to set (overrides bump_type)",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Don't create git commit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Find pyproject.toml
    repo_root = Path(__file__).parent.parent
    pyproject_path = repo_root / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found", file=sys.stderr)
        return 1

    # Get current version
    current_version = get_current_version(pyproject_path)
    print(f"Current version: {current_version}")

    # Calculate new version
    if args.version:
        new_version = args.version
        # Validate format
        try:
            parse_version(new_version)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        new_version = bump_version(current_version, args.bump_type)

    print(f"New version: {new_version}")

    # Check if tag already exists
    tag = f"v{new_version}"
    if check_tag_exists(tag):
        print(f"Warning: Tag {tag} already exists!", file=sys.stderr)
        response = input("Continue anyway? [y/N] ")
        if response.lower() != "y":
            return 1

    if args.dry_run:
        print("\nDry run - no changes made")
        return 0

    # Update version
    update_version(pyproject_path, new_version)
    print(f"Updated {pyproject_path}")

    # Create git commit
    if not args.no_commit:
        if not check_git_status():
            print("\nWarning: Git working directory is not clean")
            response = input("Continue with commit? [y/N] ")
            if response.lower() != "y":
                return 1

        try:
            subprocess.run(
                ["git", "add", str(pyproject_path)],
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"chore: bump version to {new_version}"],
                check=True,
            )
            print(f"\nCreated commit: chore: bump version to {new_version}")
            print("\nNext steps:")
            print("1. Push to remote: git push origin <branch>")
            print("2. Create PR and merge to main")
            print(f"3. Auto-tag workflow will create tag {tag}")
            print("4. Publish workflow will release to PyPI")
        except subprocess.CalledProcessError as e:
            print(f"Error creating commit: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

