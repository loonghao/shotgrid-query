"""Pydantic models for ShotGrid query builder.

This module provides Pydantic models for ShotGrid API data types and filters.
"""

import logging
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TimeUnit(str, Enum):
    """ShotGrid time unit."""

    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class FilterOperator(str, Enum):
    """ShotGrid filter operators."""

    IS = "is"
    IS_NOT = "is_not"
    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    IN = "in"
    NOT_IN = "not_in"
    IN_LAST = "in_last"
    NOT_IN_LAST = "not_in_last"
    IN_NEXT = "in_next"
    NOT_IN_NEXT = "not_in_next"
    IN_CALENDAR_DAY = "in_calendar_day"
    IN_CALENDAR_WEEK = "in_calendar_week"
    IN_CALENDAR_MONTH = "in_calendar_month"
    IN_CALENDAR_YEAR = "in_calendar_year"
    TYPE_IS = "type_is"
    TYPE_IS_NOT = "type_is_not"
    NAME_CONTAINS = "name_contains"
    NAME_NOT_CONTAINS = "name_not_contains"
    NAME_IS = "name_is"


class EntityRef(BaseModel):
    """ShotGrid entity reference."""

    model_config = ConfigDict(extra="allow")

    type: str
    id: int
    name: str | None = None


class Filter(BaseModel):
    """ShotGrid filter model."""

    field: str
    operator: FilterOperator
    value: Any

    @model_validator(mode="after")
    def validate_time_filter(self) -> "Filter":
        """Validate time filter values."""
        operator = self.operator
        value = self.value

        if operator in [
            FilterOperator.IN_LAST,
            FilterOperator.NOT_IN_LAST,
            FilterOperator.IN_NEXT,
            FilterOperator.NOT_IN_NEXT,
        ]:
            if isinstance(value, str) and " " in value:
                # Will be processed later
                pass
            elif isinstance(value, list) and len(value) == 2:
                count, unit = value
                if not isinstance(count, int):
                    raise ValueError(f"Time filter count must be an integer, got {type(count).__name__}")

                if unit not in [u.value for u in TimeUnit]:
                    raise ValueError(f"Invalid time unit: {unit}. Must be one of {[u.value for u in TimeUnit]}")
            else:
                raise ValueError("Time filter value must be [number, 'UNIT'] or 'number unit'")

        if operator in [FilterOperator.BETWEEN, FilterOperator.NOT_BETWEEN]:
            if not isinstance(value, list) or len(value) != 2:
                raise ValueError("Between filter value must be a list with exactly 2 elements [min, max]")

        return self

    def to_tuple(self) -> tuple[str, str, Any]:
        """Convert to tuple format for ShotGrid API."""
        return (self.field, self.operator.value, self.value)

    @classmethod
    def from_tuple(cls, filter_tuple: tuple[str, str, Any]) -> "Filter":
        """Create from tuple format."""
        field, operator, value = filter_tuple
        return cls(field=field, operator=FilterOperator(operator), value=value)


class FilterRequest(BaseModel):
    """Filter model for API requests.

    This model is more flexible and can handle different formats of filter inputs.
    """

    field: str
    operator: str  # Use string instead of enum for more flexibility
    value: Any

    def to_filter(self) -> Filter:
        """Convert to Filter model."""
        try:
            # Try to convert operator to FilterOperator enum
            filter_operator = FilterOperator(self.operator)
            return Filter(field=self.field, operator=filter_operator, value=self.value)
        except ValueError:
            # If conversion fails, log a warning and use the string value
            logging.warning(f"Unknown filter operator: {self.operator}. Using as string.")
            return Filter(field=self.field, operator=self.operator, value=self.value)  # type: ignore

    @classmethod
    def from_dict(cls, filter_dict: dict[str, Any]) -> "FilterRequest":
        """Create from dictionary."""
        field: str = filter_dict.get("field", "")
        operator: str = filter_dict.get("operator", "")
        value: Any = filter_dict.get("value")
        return cls(field=field, operator=operator, value=value)


class TimeFilter(BaseModel):
    """ShotGrid time filter."""

    field: str
    operator: Literal["in_last", "not_in_last", "in_next", "not_in_next"]
    count: int = Field(..., gt=0)
    unit: TimeUnit

    def to_filter(self) -> Filter:
        """Convert to Filter model."""
        return Filter(
            field=self.field,
            operator=self.operator,  # type: ignore
            value=[self.count, self.unit.value],
        )
