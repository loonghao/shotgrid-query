"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_entity_ref():
    """Sample entity reference for testing."""
    return {"type": "Project", "id": 123}


@pytest.fixture
def sample_filters():
    """Sample filters for testing."""
    return [
        ["sg_status_list", "is", "ip"],
        ["project", "is", {"type": "Project", "id": 123}],
        ["created_at", "in_last", [7, "DAY"]],
    ]
