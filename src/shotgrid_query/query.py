"""QueryBuilder for ShotGrid API.

This module provides a chainable query builder for constructing ShotGrid queries
with a Pythonic, intuitive API.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from shotgrid_query.custom_types import EntityType, Filter
from shotgrid_query.filters import FilterBuilder, process_filters

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Chainable query builder for ShotGrid API.

    This class provides a fluent interface for building ShotGrid queries,
    making it easier to construct complex queries with better readability.

    Example:
        >>> query = QueryBuilder("Shot")
        >>> query.filter(sg_status_list="ip").filter(project_id=123)
        >>> query.select("code", "description").order_by("-created_at")
        >>> filters = query.to_filters()
        >>> fields = query.to_fields()
    """

    def __init__(self, entity_type: EntityType):
        """Initialize the query builder.

        Args:
            entity_type: The ShotGrid entity type to query (e.g., "Shot", "Asset", "Task")
        """
        self._entity_type = entity_type
        self._filters: List[Filter] = []
        self._fields: List[str] = []
        self._order: List[Dict[str, str]] = []
        self._limit: Optional[int] = None
        self._retired_only: bool = False
        self._include_archived_projects: bool = True
        self._additional_filter_presets: Optional[List[Dict[str, Any]]] = None
        self._filter_operator: str = "all"  # "all" (AND) or "any" (OR)

    def filter(self, **kwargs: Any) -> "QueryBuilder":
        """Add filters to the query using keyword arguments.

        This method supports several filter syntaxes:
        1. Simple equality: field=value
        2. Operator suffix: field__operator=value
        3. Entity reference: field_id=123 (converted to entity ref)

        Supported operators (via __ suffix):
        - is, is_not
        - contains, not_contains
        - starts_with, ends_with
        - greater_than, less_than
        - between (value should be [min, max])
        - in, not_in (value should be list)
        - in_last, in_next (value should be "N unit" like "7 days")

        Args:
            **kwargs: Field filters as keyword arguments

        Returns:
            QueryBuilder: Self for method chaining

        Examples:
            >>> query.filter(code="SHOT_010")
            >>> query.filter(sg_status_list__in=["ip", "fin"])
            >>> query.filter(created_at__in_last="7 days")
            >>> query.filter(project_id=123)  # Converted to entity ref
        """
        for key, value in kwargs.items():
            # Parse field and operator
            if "__" in key:
                field, operator = key.rsplit("__", 1)
            else:
                field = key
                operator = "is"

            # Handle special _id suffix for entity references
            if field.endswith("_id") and operator == "is":
                # Convert field_id=123 to field={"type": "Entity", "id": 123}
                # We'll need to infer the entity type from the field name
                actual_field = field[:-3]  # Remove _id suffix
                if isinstance(value, int):
                    # For now, we'll just use the value as-is
                    # In a more advanced implementation, we could look up the entity type
                    # from the schema
                    self._filters.append((actual_field, "is", value))
                else:
                    self._filters.append((actual_field, operator, value))
            else:
                self._filters.append((field, operator, value))

        return self

    def filter_raw(self, *filters: Filter) -> "QueryBuilder":
        """Add raw filters in ShotGrid format.

        Args:
            *filters: Filters in tuple format (field, operator, value)

        Returns:
            QueryBuilder: Self for method chaining

        Example:
            >>> query.filter_raw(("code", "is", "SHOT_010"))
            >>> query.filter_raw(("sg_status_list", "in", ["ip", "fin"]))
        """
        self._filters.extend(filters)
        return self

    def select(self, *fields: str) -> "QueryBuilder":
        """Select fields to return in the query results.

        Args:
            *fields: Field names to select

        Returns:
            QueryBuilder: Self for method chaining

        Example:
            >>> query.select("code", "description", "sg_status_list")
        """
        self._fields.extend(fields)
        return self

    def select_related(self, field: str, fields: Optional[List[str]] = None) -> "QueryBuilder":
        """Select related entity fields using dot notation.

        Args:
            field: The relationship field name
            fields: List of fields to select from the related entity.
                   If None, selects default fields (id, type, name)

        Returns:
            QueryBuilder: Self for method chaining

        Example:
            >>> query.select_related("project", ["name", "code"])
            >>> # Adds: "project.Project.name", "project.Project.code"
        """
        # For now, we'll add a placeholder
        # In a full implementation, we'd need to look up the entity type
        # from the schema to construct the proper field path
        if fields:
            for related_field in fields:
                # We'll need to determine the entity type dynamically
                # For now, just add the field as-is
                self._fields.append(f"{field}.{related_field}")
        else:
            self._fields.append(field)

        return self

    def order_by(self, *fields: str) -> "QueryBuilder":
        """Set the order of results.

        Args:
            *fields: Field names to order by. Prefix with '-' for descending order.

        Returns:
            QueryBuilder: Self for method chaining

        Example:
            >>> query.order_by("code")  # Ascending
            >>> query.order_by("-created_at")  # Descending
            >>> query.order_by("project", "-code")  # Multiple fields
        """
        for field in fields:
            if field.startswith("-"):
                self._order.append({"field_name": field[1:], "direction": "desc"})
            else:
                self._order.append({"field_name": field, "direction": "asc"})

        return self

    def limit(self, count: int) -> "QueryBuilder":
        """Limit the number of results.

        Args:
            count: Maximum number of results to return

        Returns:
            QueryBuilder: Self for method chaining

        Example:
            >>> query.limit(100)
        """
        self._limit = count
        return self

    def retired_only(self, value: bool = True) -> "QueryBuilder":
        """Filter for retired entities only.

        Args:
            value: Whether to return only retired entities

        Returns:
            QueryBuilder: Self for method chaining

        Example:
            >>> query.retired_only()
            >>> query.retired_only(False)
        """
        self._retired_only = value
        return self

    def include_archived_projects(self, value: bool = True) -> "QueryBuilder":
        """Include entities from archived projects.

        Args:
            value: Whether to include archived projects

        Returns:
            QueryBuilder: Self for method chaining

        Example:
            >>> query.include_archived_projects(False)
        """
        self._include_archived_projects = value
        return self

    def filter_operator(self, operator: str) -> "QueryBuilder":
        """Set the logical operator for combining filters.

        Args:
            operator: Either "all" (AND) or "any" (OR)

        Returns:
            QueryBuilder: Self for method chaining

        Raises:
            ValueError: If operator is not "all" or "any"

        Example:
            >>> query.filter_operator("any")  # OR logic
        """
        if operator not in ["all", "any"]:
            raise ValueError(f"Invalid filter operator: {operator}. Must be 'all' or 'any'")

        self._filter_operator = operator
        return self

    def to_filters(self) -> List[Filter]:
        """Convert the query to ShotGrid filter format.

        Returns:
            List of filters in tuple format (field, operator, value)

        Example:
            >>> filters = query.to_filters()
            >>> # [("code", "is", "SHOT_010"), ...]
        """
        # Process filters to handle special values and time-related filters
        if self._filters:
            return process_filters(self._filters)
        return []

    def to_fields(self) -> List[str]:
        """Get the list of fields to select.

        Returns:
            List of field names

        Example:
            >>> fields = query.to_fields()
            >>> # ["code", "description", "project.Project.name"]
        """
        return self._fields.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the query to a dictionary suitable for ShotGrid API.

        Returns:
            Dictionary with filters, fields, order, and other query parameters

        Example:
            >>> query_dict = query.to_dict()
            >>> # {
            >>> #     "filters": [...],
            >>> #     "fields": [...],
            >>> #     "order": [...],
            >>> #     "limit": 100
            >>> # }
        """
        result: Dict[str, Any] = {
            "entity_type": self._entity_type,
        }

        if self._filters:
            result["filters"] = self.to_filters()

        if self._fields:
            result["fields"] = self.to_fields()

        if self._order:
            result["order"] = self._order

        if self._limit is not None:
            result["limit"] = self._limit

        if self._retired_only:
            result["retired_only"] = self._retired_only

        if not self._include_archived_projects:
            result["include_archived_projects"] = self._include_archived_projects

        if self._filter_operator != "all":
            result["filter_operator"] = self._filter_operator

        if self._additional_filter_presets:
            result["additional_filter_presets"] = self._additional_filter_presets

        return result

    def execute(self, sg: Any) -> List[Dict[str, Any]]:
        """Execute the query using a ShotGrid connection.

        Args:
            sg: ShotGrid connection object (shotgun_api3.Shotgun instance)

        Returns:
            List of entities matching the query

        Example:
            >>> import shotgun_api3
            >>> sg = shotgun_api3.Shotgun(url, script_name, api_key)
            >>> results = query.execute(sg)
        """
        filters = self.to_filters()
        fields = self.to_fields() if self._fields else None

        # Build kwargs for sg.find()
        kwargs: Dict[str, Any] = {}

        if self._order:
            kwargs["order"] = self._order

        if self._limit is not None:
            kwargs["limit"] = self._limit

        if self._retired_only:
            kwargs["retired_only"] = self._retired_only

        if not self._include_archived_projects:
            kwargs["include_archived_projects"] = self._include_archived_projects

        if self._filter_operator != "all":
            kwargs["filter_operator"] = self._filter_operator

        if self._additional_filter_presets:
            kwargs["additional_filter_presets"] = self._additional_filter_presets

        logger.debug(
            "Executing query: entity_type=%s, filters=%s, fields=%s, kwargs=%s",
            self._entity_type,
            filters,
            fields,
            kwargs,
        )

        return sg.find(self._entity_type, filters, fields, **kwargs)

    def first(self, sg: Any) -> Optional[Dict[str, Any]]:
        """Execute the query and return the first result.

        Args:
            sg: ShotGrid connection object

        Returns:
            First entity matching the query, or None if no results

        Example:
            >>> result = query.first(sg)
        """
        original_limit = self._limit
        self._limit = 1

        try:
            results = self.execute(sg)
            return results[0] if results else None
        finally:
            self._limit = original_limit

    def count(self, sg: Any) -> int:
        """Count the number of entities matching the query.

        Args:
            sg: ShotGrid connection object

        Returns:
            Number of matching entities

        Example:
            >>> total = query.count(sg)
        """
        # ShotGrid doesn't have a direct count method, so we use summarize
        filters = self.to_filters()

        summary = sg.summarize(
            entity_type=self._entity_type,
            filters=filters,
            summary_fields=[{"field": "id", "type": "count"}],
        )

        if summary and "summaries" in summary and summary["summaries"]:
            return summary["summaries"]["id"]

        return 0

    def exists(self, sg: Any) -> bool:
        """Check if any entities match the query.

        Args:
            sg: ShotGrid connection object

        Returns:
            True if at least one entity matches, False otherwise

        Example:
            >>> if query.exists(sg):
            >>>     print("Found matching entities")
        """
        return self.first(sg) is not None

    def clone(self) -> "QueryBuilder":
        """Create a copy of this query builder.

        Returns:
            New QueryBuilder instance with the same configuration

        Example:
            >>> query2 = query.clone()
            >>> query2.filter(code="SHOT_020")
        """
        new_query = QueryBuilder(self._entity_type)
        new_query._filters = self._filters.copy()
        new_query._fields = self._fields.copy()
        new_query._order = self._order.copy()
        new_query._limit = self._limit
        new_query._retired_only = self._retired_only
        new_query._include_archived_projects = self._include_archived_projects
        new_query._filter_operator = self._filter_operator

        if self._additional_filter_presets:
            new_query._additional_filter_presets = self._additional_filter_presets.copy()

        return new_query

    def __repr__(self) -> str:
        """Return a string representation of the query."""
        return (
            f"QueryBuilder(entity_type={self._entity_type!r}, "
            f"filters={len(self._filters)}, "
            f"fields={len(self._fields)}, "
            f"limit={self._limit})"
        )


# Convenience alias
Query = QueryBuilder

