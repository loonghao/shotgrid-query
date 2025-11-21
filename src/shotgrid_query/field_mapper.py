"""Field mapping utilities for ShotGrid queries.

This module provides utilities for mapping and resolving field paths,
especially for related entity fields using dot notation.
"""

import logging
from typing import Dict, List, Optional, Set

from shotgrid_query.custom_types import EntityType

logger = logging.getLogger(__name__)


class FieldMapper:
    """Utility class for mapping and resolving ShotGrid field paths.

    This class helps with:
    1. Converting simple field names to ShotGrid's deep query format
    2. Resolving related entity fields (e.g., "project.name" -> "project.Project.name")
    3. Managing field dependencies and relationships
    """

    def __init__(self, entity_type: EntityType, schema: Optional[Dict] = None):
        """Initialize the field mapper.

        Args:
            entity_type: The entity type being queried
            schema: Optional ShotGrid schema dictionary for field resolution
        """
        self._entity_type = entity_type
        self._schema = schema or {}
        self._field_cache: Dict[str, str] = {}

    def resolve_field(self, field: str) -> str:
        """Resolve a field path to ShotGrid's format.

        This method converts simplified field paths to ShotGrid's deep query format.
        For example:
        - "code" -> "code"
        - "project.name" -> "project.Project.name" (if schema available)
        - "project.Project.name" -> "project.Project.name" (already resolved)

        Args:
            field: Field path to resolve

        Returns:
            Resolved field path in ShotGrid format
        """
        # Check cache first
        if field in self._field_cache:
            return self._field_cache[field]

        # If field doesn't contain a dot, it's a simple field
        if "." not in field:
            self._field_cache[field] = field
            return field

        # Split the field path
        parts = field.split(".")

        # If it's already in ShotGrid format (field.EntityType.field), return as-is
        if len(parts) == 3:
            self._field_cache[field] = field
            return field

        # If it's in simplified format (field.field), try to resolve the entity type
        if len(parts) == 2:
            relationship_field, related_field = parts

            # Try to get entity type from schema
            entity_type = self._get_related_entity_type(relationship_field)

            if entity_type:
                resolved = f"{relationship_field}.{entity_type}.{related_field}"
                self._field_cache[field] = resolved
                logger.debug("Resolved field %s to %s", field, resolved)
                return resolved
            else:
                # If we can't resolve, return as-is and log a warning
                logger.warning(
                    "Could not resolve entity type for field %s on %s. "
                    "Returning as-is. Consider providing a schema.",
                    relationship_field,
                    self._entity_type,
                )
                self._field_cache[field] = field
                return field

        # For other formats, return as-is
        self._field_cache[field] = field
        return field

    def resolve_fields(self, fields: List[str]) -> List[str]:
        """Resolve multiple field paths.

        Args:
            fields: List of field paths to resolve

        Returns:
            List of resolved field paths
        """
        return [self.resolve_field(field) for field in fields]

    def _get_related_entity_type(self, field: str) -> Optional[str]:
        """Get the entity type for a related field.

        Args:
            field: The relationship field name

        Returns:
            Entity type name, or None if not found
        """
        if not self._schema:
            return None

        # Try to get field info from schema
        entity_schema = self._schema.get(self._entity_type, {})
        field_info = entity_schema.get(field, {})

        # Check if it's an entity or multi-entity field
        data_type = field_info.get("data_type", {})

        if isinstance(data_type, dict):
            # For entity fields, the data_type is a dict with 'value' key
            if data_type.get("value") == "entity":
                # Get the valid types for this field
                valid_types = field_info.get("properties", {}).get("valid_types", {}).get("value", [])
                if valid_types and len(valid_types) == 1:
                    return valid_types[0]
                elif valid_types:
                    # Multiple valid types - can't auto-resolve
                    logger.warning(
                        "Field %s on %s has multiple valid types: %s. Cannot auto-resolve.",
                        field,
                        self._entity_type,
                        valid_types,
                    )
                    return None

        return None

    def get_related_fields(self, relationship_field: str, fields: List[str]) -> List[str]:
        """Get fully qualified field paths for related entity fields.

        Args:
            relationship_field: The relationship field name (e.g., "project")
            fields: List of fields to select from the related entity

        Returns:
            List of fully qualified field paths
        """
        entity_type = self._get_related_entity_type(relationship_field)

        if entity_type:
            return [f"{relationship_field}.{entity_type}.{field}" for field in fields]
        else:
            # Fallback: return simplified format
            logger.warning(
                "Could not determine entity type for %s. Using simplified format.", relationship_field
            )
            return [f"{relationship_field}.{field}" for field in fields]

    def clear_cache(self) -> None:
        """Clear the field resolution cache."""
        self._field_cache.clear()

