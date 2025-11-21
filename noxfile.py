"""Nox sessions for testing, linting, and building."""

import nox

# Default sessions to run
nox.options.sessions = ["lint", "type_check", "tests"]

# Python versions to test
PYTHON_VERSIONS = ["3.10", "3.11", "3.12"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run the test suite with pytest."""
    session.install(".[dev]")
    session.run("pytest", *session.posargs)


@nox.session(python="3.10")
def lint(session):
    """Run ruff linter."""
    session.install("ruff")
    session.run("ruff", "check", "src", "tests", "noxfile.py")


@nox.session(python="3.10")
def format(session):
    """Format code with ruff."""
    session.install("ruff")
    session.run("ruff", "format", "src", "tests", "noxfile.py")
    session.run("ruff", "check", "--fix", "src", "tests", "noxfile.py")


@nox.session(python="3.10")
def type_check(session):
    """Run mypy type checker."""
    session.install(".[dev]")
    session.run("mypy", "src/shotgrid_query")


@nox.session(python="3.10")
def coverage(session):
    """Generate coverage report."""
    session.install(".[dev]")
    session.run("pytest", "--cov", "--cov-report=html", "--cov-report=term")


@nox.session(python="3.10")
def build(session):
    """Build the package."""
    session.install("build")
    session.run("python", "-m", "build")
