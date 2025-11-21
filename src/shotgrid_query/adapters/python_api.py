"""Python API adapter for ShotGrid queries.

This module provides an adapter for the official shotgun_api3 Python library.
"""

import logging
from typing import Any

from shotgrid_query.adapters.base import BaseAdapter
from shotgrid_query.custom_types import EntityType, Filter

logger = logging.getLogger(__name__)


class PythonAPIAdapter(BaseAdapter):
    """Adapter for the shotgun_api3 Python library.

    This adapter wraps a shotgun_api3.Shotgun instance and provides
    a consistent interface for executing queries.
    """

    def __init__(self, sg: Any):
        """Initialize the adapter.

        Args:
            sg: shotgun_api3.Shotgun instance
        """
        self._sg = sg

    def find(
        self,
        entity_type: EntityType,
        filters: list[Filter],
        fields: list[str] | None = None,
        order: list[dict[str, str]] | None = None,
        limit: int | None = None,
        retired_only: bool = False,
        include_archived_projects: bool = True,
        filter_operator: str = "all",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Find entities using shotgun_api3.

        Args:
            entity_type: The entity type to query
            filters: List of filters in tuple format
            fields: List of field names to return
            order: List of order specifications
            limit: Maximum number of results
            retired_only: Whether to return only retired entities
            include_archived_projects: Whether to include archived projects
            filter_operator: Logical operator for filters ("all" or "any")
            **kwargs: Additional parameters passed to sg.find()

        Returns:
            List of entities matching the criteria
        """
        # Build kwargs for sg.find()
        find_kwargs: dict[str, Any] = {}

        if order is not None:
            find_kwargs["order"] = order

        if limit is not None:
            find_kwargs["limit"] = limit

        if retired_only:
            find_kwargs["retired_only"] = retired_only

        if not include_archived_projects:
            find_kwargs["include_archived_projects"] = include_archived_projects

        if filter_operator != "all":
            find_kwargs["filter_operator"] = filter_operator

        # Add any additional kwargs
        find_kwargs.update(kwargs)

        logger.debug(
            "Executing find: entity_type=%s, filters=%s, fields=%s, kwargs=%s",
            entity_type,
            filters,
            fields,
            find_kwargs,
        )

        result: list[dict[str, Any]] = self._sg.find(entity_type, filters, fields, **find_kwargs)
        return result

    def find_one(
        self,
        entity_type: EntityType,
        filters: list[Filter],
        fields: list[str] | None = None,
        order: list[dict[str, str]] | None = None,
        filter_operator: str = "all",
        retired_only: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Find a single entity using shotgun_api3.

        Args:
            entity_type: The entity type to query
            filters: List of filters in tuple format
            fields: List of field names to return
            order: List of order specifications
            filter_operator: Logical operator for filters ("all" or "any")
            retired_only: Whether to return only retired entities
            **kwargs: Additional parameters passed to sg.find_one()

        Returns:
            First entity matching the criteria, or None if not found
        """
        # Build kwargs for sg.find_one()
        find_kwargs: dict[str, Any] = {}

        if order is not None:
            find_kwargs["order"] = order

        if filter_operator != "all":
            find_kwargs["filter_operator"] = filter_operator

        if retired_only:
            find_kwargs["retired_only"] = retired_only

        # Add any additional kwargs
        find_kwargs.update(kwargs)

        logger.debug(
            "Executing find_one: entity_type=%s, filters=%s, fields=%s, kwargs=%s",
            entity_type,
            filters,
            fields,
            find_kwargs,
        )

        result: dict[str, Any] | None = self._sg.find_one(entity_type, filters, fields, **find_kwargs)
        return result

    def create(
        self,
        entity_type: EntityType,
        data: dict[str, Any],
        return_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new entity using shotgun_api3.

        Args:
            entity_type: The entity type to create
            data: Dictionary of field values
            return_fields: List of fields to return in the created entity

        Returns:
            The created entity
        """
        logger.debug("Creating entity: entity_type=%s, data=%s, return_fields=%s", entity_type, data, return_fields)

        result: dict[str, Any] = self._sg.create(entity_type, data, return_fields)
        return result

    def update(
        self,
        entity_type: EntityType,
        entity_id: int,
        data: dict[str, Any],
        return_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing entity using shotgun_api3.

        Args:
            entity_type: The entity type
            entity_id: The entity ID
            data: Dictionary of field values to update
            return_fields: List of fields to return in the updated entity

        Returns:
            The updated entity
        """
        logger.debug(
            "Updating entity: entity_type=%s, entity_id=%s, data=%s, return_fields=%s",
            entity_type,
            entity_id,
            data,
            return_fields,
        )

        result: dict[str, Any] = self._sg.update(entity_type, entity_id, data, return_fields)
        return result

    def delete(self, entity_type: EntityType, entity_id: int) -> bool:
        """Delete an entity using shotgun_api3.

        Args:
            entity_type: The entity type
            entity_id: The entity ID

        Returns:
            True if successful
        """
        logger.debug("Deleting entity: entity_type=%s, entity_id=%s", entity_type, entity_id)

        result = self._sg.delete(entity_type, entity_id)
        return result is True

    def schema_field_read(self, entity_type: EntityType, field_name: str | None = None) -> dict[str, Any]:
        """Read schema information for entity fields using shotgun_api3.

        Args:
            entity_type: The entity type
            field_name: Optional specific field name. If None, returns all fields.

        Returns:
            Schema information for the field(s)
        """
        logger.debug("Reading field schema: entity_type=%s, field_name=%s", entity_type, field_name)

        result: dict[str, Any] = self._sg.schema_field_read(entity_type, field_name)
        return result

    def schema_entity_read(self) -> dict[str, Any]:
        """Read schema information for all entity types using shotgun_api3.

        Returns:
            Schema information for all entities
        """
        logger.debug("Reading entity schema")

        result: dict[str, Any] = self._sg.schema_entity_read()
        return result

    @property
    def sg(self) -> Any:
        """Get the underlying shotgun_api3.Shotgun instance.

        Returns:
            The Shotgun instance
        """
        return self._sg
