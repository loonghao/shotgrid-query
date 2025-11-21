"""Schema validation utilities for ShotGrid queries.

This module provides schema validation and caching mechanisms to ensure
queries are valid before execution.
"""

import logging
import time
from typing import Any

from shotgrid_query.constants import (
    DATA_TYPE_DATE,
    DATA_TYPE_DATE_TIME,
    DATA_TYPE_ENTITY,
    DATA_TYPE_FLOAT,
    DATA_TYPE_MULTI_ENTITY,
    DATA_TYPE_NUMBER,
    DATA_TYPE_TEXT,
    DEFAULT_FILTER_EXAMPLE,
    DEFAULT_SCHEMA_CACHE_TTL,
    FILTER_EXAMPLES,
    MAX_SUGGESTIONS,
    OPERATOR_TYPE_COMPATIBILITY,
    TIME_UNIT_DAY,
    TIME_UNIT_MONTH,
    TIME_UNIT_WEEK,
    TIME_UNIT_YEAR,
)
from shotgrid_query.custom_types import EntityType, Filter

logger = logging.getLogger(__name__)


class SchemaCache:
    """Global schema cache to avoid repeated API calls.

    This cache stores schema information with TTL (time-to-live) to balance
    between performance and freshness of schema data.
    """

    _cache: dict[str, dict[str, Any]] = {}
    _timestamps: dict[str, float] = {}
    _ttl: int = DEFAULT_SCHEMA_CACHE_TTL

    @classmethod
    def get(cls, sg: Any, entity_type: EntityType) -> dict[str, Any]:
        """Get cached schema for an entity type.

        Args:
            sg: ShotGrid connection instance
            entity_type: Entity type to get schema for

        Returns:
            Schema dictionary for the entity type
        """
        cache_key = f"{id(sg)}:{entity_type}"

        # Check if cache exists and is not expired
        if cache_key in cls._cache:
            timestamp = cls._timestamps.get(cache_key, 0)
            if time.time() - timestamp < cls._ttl:
                logger.debug("Using cached schema for %s", entity_type)
                return cls._cache[cache_key]

        # Fetch fresh schema
        logger.debug("Fetching schema for %s from ShotGrid", entity_type)
        schema: dict[str, Any] = sg.schema_field_read(entity_type)
        cls._cache[cache_key] = schema
        cls._timestamps[cache_key] = time.time()

        return schema

    @classmethod
    def set_ttl(cls, ttl: int) -> None:
        """Set the TTL for cached schemas.

        Args:
            ttl: Time-to-live in seconds
        """
        cls._ttl = ttl

    @classmethod
    def clear(cls, sg: Any | None = None, entity_type: EntityType | None = None) -> None:
        """Clear cached schemas.

        Args:
            sg: Optional ShotGrid connection. If provided, only clear cache for this connection.
            entity_type: Optional entity type. If provided, only clear cache for this type.
        """
        if sg is None and entity_type is None:
            # Clear all cache
            cls._cache.clear()
            cls._timestamps.clear()
            logger.debug("Cleared all schema cache")
        elif sg is not None and entity_type is not None:
            # Clear specific cache entry
            cache_key = f"{id(sg)}:{entity_type}"
            cls._cache.pop(cache_key, None)
            cls._timestamps.pop(cache_key, None)
            logger.debug("Cleared schema cache for %s", entity_type)
        elif sg is not None:
            # Clear all cache for this connection
            sg_id = id(sg)
            keys_to_remove = [key for key in cls._cache if key.startswith(f"{sg_id}:")]
            for key in keys_to_remove:
                cls._cache.pop(key, None)
                cls._timestamps.pop(key, None)
            logger.debug("Cleared schema cache for connection %s", sg_id)


class ValidationError:
    """Represents a validation error with detailed information."""

    def __init__(self, field: str, message: str, suggestion: str | None = None):
        """Initialize validation error.

        Args:
            field: Field name that caused the error
            message: Error message
            suggestion: Optional suggestion for fixing the error
        """
        self.field = field
        self.message = message
        self.suggestion = suggestion

    def __str__(self) -> str:
        """Get formatted error message."""
        error_msg = f"Field '{self.field}': {self.message}"
        if self.suggestion:
            error_msg += f"\n  💡 Suggestion: {self.suggestion}"
        return error_msg

    def __repr__(self) -> str:
        """Get representation of error."""
        return f"ValidationError(field={self.field!r}, message={self.message!r})"


# Note: OPERATOR_TYPE_COMPATIBILITY is imported from constants module


def is_operator_valid_for_type(operator: str, field_type: str) -> bool:
    """Check if an operator is valid for a field type.

    Args:
        operator: Filter operator
        field_type: ShotGrid field data type

    Returns:
        True if operator is compatible with field type
    """
    if operator not in OPERATOR_TYPE_COMPATIBILITY:
        # Unknown operator, let ShotGrid handle it
        return True

    compatible_types = OPERATOR_TYPE_COMPATIBILITY[operator]
    return field_type in compatible_types


def get_operator_suggestion(field_type: str) -> str:
    """Get suggested operators for a field type.

    Args:
        field_type: ShotGrid field data type

    Returns:
        Comma-separated list of suggested operators
    """
    suggested_ops = [op for op, types in OPERATOR_TYPE_COMPATIBILITY.items() if field_type in types]
    return ", ".join(sorted(suggested_ops[:10]))  # Limit to 10 suggestions


def validate_filter_value_type(value: Any, field_info: dict[str, Any], operator: str) -> tuple[bool, str | None]:
    """Validate that a filter value matches the expected type.

    Args:
        value: Filter value
        field_info: Field schema information
        operator: Filter operator

    Returns:
        Tuple of (is_valid, error_message)
    """
    field_type = field_info.get("data_type", {}).get("value")

    # Special handling for None values
    if value is None:
        return True, None

    # Entity field validation
    if field_type == DATA_TYPE_ENTITY:
        if operator in ["is", "is_not"]:
            if not isinstance(value, dict) or "type" not in value or "id" not in value:
                return False, f"Entity value must be a dict with 'type' and 'id' keys, got {type(value).__name__}"

            # Check if entity type is valid
            valid_types = field_info.get("properties", {}).get("valid_types", {}).get("value", [])
            if valid_types and value.get("type") not in valid_types:
                return False, f"Entity type '{value.get('type')}' is not valid. Valid types: {', '.join(valid_types)}"

        elif operator in ["in", "not_in"]:
            if not isinstance(value, list):
                return False, f"Value for 'in' operator must be a list, got {type(value).__name__}"

    # Multi-entity field validation
    elif field_type == DATA_TYPE_MULTI_ENTITY:
        if operator in ["is", "is_not", "in", "not_in"]:
            if isinstance(value, dict):
                if "type" not in value or "id" not in value:
                    return False, "Multi-entity value must be a dict with 'type' and 'id' keys"
            elif isinstance(value, list):
                for item in value:
                    if not isinstance(item, dict) or "type" not in item or "id" not in item:
                        return False, "Multi-entity list items must be dicts with 'type' and 'id' keys"

    # Number field validation
    elif field_type in [DATA_TYPE_NUMBER, DATA_TYPE_FLOAT]:
        if operator in ["is", "is_not", "greater_than", "less_than"]:
            if not isinstance(value, (int, float)):
                return False, f"Value must be a number, got {type(value).__name__}"
        elif operator in ["between", "not_between"]:
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                return False, "Value for 'between' must be a list with 2 numbers [min, max]"

    # Text field validation
    elif field_type == DATA_TYPE_TEXT:
        if operator in ["is", "is_not", "contains", "not_contains", "starts_with", "ends_with"]:
            if not isinstance(value, str):
                return False, f"Value must be a string, got {type(value).__name__}"

    # Date/DateTime field validation
    elif field_type in [DATA_TYPE_DATE, DATA_TYPE_DATE_TIME]:
        if operator in ["in_last", "not_in_last", "in_next", "not_in_next"]:
            if isinstance(value, str):
                # String format like "7 days" - will be processed later
                pass
            elif isinstance(value, list) and len(value) == 2:
                count, unit = value
                if not isinstance(count, int):
                    return False, f"Time filter count must be an integer, got {type(count).__name__}"
                if unit not in [TIME_UNIT_DAY, TIME_UNIT_WEEK, TIME_UNIT_MONTH, TIME_UNIT_YEAR]:
                    return False, f"Time filter unit must be one of {TIME_UNIT_DAY}, {TIME_UNIT_WEEK}, {TIME_UNIT_MONTH}, {TIME_UNIT_YEAR}, got {unit}"
            else:
                return False, "Time filter value must be [count, 'UNIT'] or 'count unit' string"

    return True, None


def validate_field_exists(field: str, schema: dict[str, Any], entity_type: EntityType) -> ValidationError | None:
    """Validate that a field exists in the schema.

    Args:
        field: Field name (may include dots for related fields)
        schema: Entity schema dictionary
        entity_type: Entity type being queried

    Returns:
        ValidationError if field doesn't exist, None otherwise
    """
    # Handle related fields (e.g., "project.Project.name")
    base_field = field.split(".")[0]

    if base_field not in schema:
        # Get available fields for suggestion
        available_fields = sorted(schema.keys())[:MAX_SUGGESTIONS]
        suggestion = f"Available fields: {', '.join(available_fields)}"
        if len(schema) > MAX_SUGGESTIONS:
            suggestion += f" (and {len(schema) - MAX_SUGGESTIONS} more)"

        return ValidationError(
            field=field,
            message=f"Field does not exist in {entity_type}",
            suggestion=suggestion,
        )

    return None


def validate_filters(
    filters: list[Filter], schema: dict[str, Any], entity_type: EntityType
) -> list[ValidationError]:
    """Validate a list of filters against schema.

    Args:
        filters: List of filters to validate
        schema: Entity schema dictionary
        entity_type: Entity type being queried

    Returns:
        List of validation errors (empty if all valid)
    """
    errors: list[ValidationError] = []

    for field, operator, value in filters:
        # Check if field exists
        field_error = validate_field_exists(field, schema, entity_type)
        if field_error:
            errors.append(field_error)
            continue

        # Get base field for schema lookup
        base_field = field.split(".")[0]
        field_info = schema[base_field]
        field_type = field_info.get("data_type", {}).get("value", "unknown")

        # Check if operator is valid for field type
        if not is_operator_valid_for_type(operator, field_type):
            suggestion = f"Valid operators for {field_type} fields: {get_operator_suggestion(field_type)}"
            errors.append(
                ValidationError(
                    field=field,
                    message=f"Operator '{operator}' is not valid for field type '{field_type}'",
                    suggestion=suggestion,
                )
            )
            continue

        # Validate value type
        is_valid, error_msg = validate_filter_value_type(value, field_info, operator)
        if not is_valid:
            # Provide example of correct usage
            example = _get_filter_example(field, operator, field_type)
            errors.append(
                ValidationError(
                    field=field,
                    message=error_msg or "Invalid value type",
                    suggestion=f"Example: {example}",
                )
            )

    return errors


def validate_fields(fields: list[str], schema: dict[str, Any], entity_type: EntityType) -> list[ValidationError]:
    """Validate a list of fields against schema.

    Args:
        fields: List of field names to validate
        schema: Entity schema dictionary
        entity_type: Entity type being queried

    Returns:
        List of validation errors (empty if all valid)
    """
    errors: list[ValidationError] = []

    for field in fields:
        field_error = validate_field_exists(field, schema, entity_type)
        if field_error:
            errors.append(field_error)

    return errors


def _get_filter_example(field: str, operator: str, field_type: str) -> str:
    """Get an example of correct filter usage.

    Args:
        field: Field name
        operator: Filter operator
        field_type: Field data type

    Returns:
        Example filter code
    """
    # Get example template from constants
    type_examples = FILTER_EXAMPLES.get(field_type, {})
    example_template = type_examples.get(operator, DEFAULT_FILTER_EXAMPLE)

    # Replace {field} and {operator} placeholders
    return example_template.format(field=field, operator=operator)



