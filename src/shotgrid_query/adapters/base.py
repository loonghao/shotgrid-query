"""Base adapter interface for ShotGrid queries.

This module defines the base interface that all ShotGrid adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any

from shotgrid_query.custom_types import EntityType, Filter


class BaseAdapter(ABC):
    """Abstract base class for ShotGrid query adapters.

    Adapters provide a consistent interface for executing queries
    against different ShotGrid API implementations.
    """

    @abstractmethod
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
        """Find entities matching the given criteria.

        Args:
            entity_type: The entity type to query
            filters: List of filters in tuple format
            fields: List of field names to return
            order: List of order specifications
            limit: Maximum number of results
            retired_only: Whether to return only retired entities
            include_archived_projects: Whether to include archived projects
            filter_operator: Logical operator for filters ("all" or "any")
            **kwargs: Additional adapter-specific parameters

        Returns:
            List of entities matching the criteria
        """
        pass

    @abstractmethod
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
        """Find a single entity matching the given criteria.

        Args:
            entity_type: The entity type to query
            filters: List of filters in tuple format
            fields: List of field names to return
            order: List of order specifications
            filter_operator: Logical operator for filters ("all" or "any")
            retired_only: Whether to return only retired entities
            **kwargs: Additional adapter-specific parameters

        Returns:
            First entity matching the criteria, or None if not found
        """
        pass

    @abstractmethod
    def create(
        self,
        entity_type: EntityType,
        data: dict[str, Any],
        return_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new entity.

        Args:
            entity_type: The entity type to create
            data: Dictionary of field values
            return_fields: List of fields to return in the created entity

        Returns:
            The created entity
        """
        pass

    @abstractmethod
    def update(
        self,
        entity_type: EntityType,
        entity_id: int,
        data: dict[str, Any],
        return_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing entity.

        Args:
            entity_type: The entity type
            entity_id: The entity ID
            data: Dictionary of field values to update
            return_fields: List of fields to return in the updated entity

        Returns:
            The updated entity
        """
        pass

    @abstractmethod
    def delete(self, entity_type: EntityType, entity_id: int) -> bool:
        """Delete an entity.

        Args:
            entity_type: The entity type
            entity_id: The entity ID

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def schema_field_read(self, entity_type: EntityType, field_name: str | None = None) -> dict[str, Any]:
        """Read schema information for entity fields.

        Args:
            entity_type: The entity type
            field_name: Optional specific field name. If None, returns all fields.

        Returns:
            Schema information for the field(s)
        """
        pass

    @abstractmethod
    def schema_entity_read(self) -> dict[str, Any]:
        """Read schema information for all entity types.

        Returns:
            Schema information for all entities
        """
        pass
