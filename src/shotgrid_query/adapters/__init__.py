"""Adapters for different ShotGrid API interfaces.

This module provides adapters for executing queries against different
ShotGrid API implementations.
"""

from shotgrid_query.adapters.base import BaseAdapter

try:
    from shotgrid_query.adapters.python_api import PythonAPIAdapter

    __all__ = ["BaseAdapter", "PythonAPIAdapter"]
except ImportError:
    # shotgun_api3 not installed
    __all__ = ["BaseAdapter"]

