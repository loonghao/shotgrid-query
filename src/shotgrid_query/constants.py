"""Global constants for ShotGrid query operations.

This module centralizes all constants used across the library for better
maintainability and extensibility.
"""

from typing import Final

# ============================================================================
# ShotGrid Data Types
# ============================================================================

# Core data types
DATA_TYPE_TEXT: Final[str] = "text"
DATA_TYPE_NUMBER: Final[str] = "number"
DATA_TYPE_FLOAT: Final[str] = "float"
DATA_TYPE_CHECKBOX: Final[str] = "checkbox"
DATA_TYPE_ENTITY: Final[str] = "entity"
DATA_TYPE_MULTI_ENTITY: Final[str] = "multi_entity"
DATA_TYPE_DATE: Final[str] = "date"
DATA_TYPE_DATE_TIME: Final[str] = "date_time"
DATA_TYPE_STATUS_LIST: Final[str] = "status_list"
DATA_TYPE_LIST: Final[str] = "list"
DATA_TYPE_IMAGE: Final[str] = "image"
DATA_TYPE_URL: Final[str] = "url"
DATA_TYPE_DURATION: Final[str] = "duration"
DATA_TYPE_TIMECODE: Final[str] = "timecode"

# All supported data types
ALL_DATA_TYPES: Final[tuple[str, ...]] = (
    DATA_TYPE_TEXT,
    DATA_TYPE_NUMBER,
    DATA_TYPE_FLOAT,
    DATA_TYPE_CHECKBOX,
    DATA_TYPE_ENTITY,
    DATA_TYPE_MULTI_ENTITY,
    DATA_TYPE_DATE,
    DATA_TYPE_DATE_TIME,
    DATA_TYPE_STATUS_LIST,
    DATA_TYPE_LIST,
    DATA_TYPE_IMAGE,
    DATA_TYPE_URL,
    DATA_TYPE_DURATION,
    DATA_TYPE_TIMECODE,
)

# ============================================================================
# Filter Operators
# ============================================================================

# Comparison operators
OP_IS: Final[str] = "is"
OP_IS_NOT: Final[str] = "is_not"
OP_CONTAINS: Final[str] = "contains"
OP_NOT_CONTAINS: Final[str] = "not_contains"
OP_STARTS_WITH: Final[str] = "starts_with"
OP_ENDS_WITH: Final[str] = "ends_with"
OP_GREATER_THAN: Final[str] = "greater_than"
OP_LESS_THAN: Final[str] = "less_than"
OP_BETWEEN: Final[str] = "between"
OP_NOT_BETWEEN: Final[str] = "not_between"
OP_IN: Final[str] = "in"
OP_NOT_IN: Final[str] = "not_in"

# Time-based operators
OP_IN_LAST: Final[str] = "in_last"
OP_NOT_IN_LAST: Final[str] = "not_in_last"
OP_IN_NEXT: Final[str] = "in_next"
OP_NOT_IN_NEXT: Final[str] = "not_in_next"
OP_IN_CALENDAR_DAY: Final[str] = "in_calendar_day"
OP_IN_CALENDAR_WEEK: Final[str] = "in_calendar_week"
OP_IN_CALENDAR_MONTH: Final[str] = "in_calendar_month"
OP_IN_CALENDAR_YEAR: Final[str] = "in_calendar_year"

# Entity-specific operators
OP_TYPE_IS: Final[str] = "type_is"
OP_TYPE_IS_NOT: Final[str] = "type_is_not"
OP_NAME_CONTAINS: Final[str] = "name_contains"
OP_NAME_NOT_CONTAINS: Final[str] = "name_not_contains"
OP_NAME_IS: Final[str] = "name_is"

# All supported operators
ALL_OPERATORS: Final[tuple[str, ...]] = (
    OP_IS,
    OP_IS_NOT,
    OP_CONTAINS,
    OP_NOT_CONTAINS,
    OP_STARTS_WITH,
    OP_ENDS_WITH,
    OP_GREATER_THAN,
    OP_LESS_THAN,
    OP_BETWEEN,
    OP_NOT_BETWEEN,
    OP_IN,
    OP_NOT_IN,
    OP_IN_LAST,
    OP_NOT_IN_LAST,
    OP_IN_NEXT,
    OP_NOT_IN_NEXT,
    OP_IN_CALENDAR_DAY,
    OP_IN_CALENDAR_WEEK,
    OP_IN_CALENDAR_MONTH,
    OP_IN_CALENDAR_YEAR,
    OP_TYPE_IS,
    OP_TYPE_IS_NOT,
    OP_NAME_CONTAINS,
    OP_NAME_NOT_CONTAINS,
    OP_NAME_IS,
)

# ============================================================================
# Time Units
# ============================================================================

TIME_UNIT_DAY: Final[str] = "DAY"
TIME_UNIT_WEEK: Final[str] = "WEEK"
TIME_UNIT_MONTH: Final[str] = "MONTH"
TIME_UNIT_YEAR: Final[str] = "YEAR"

ALL_TIME_UNITS: Final[tuple[str, ...]] = (
    TIME_UNIT_DAY,
    TIME_UNIT_WEEK,
    TIME_UNIT_MONTH,
    TIME_UNIT_YEAR,
)

# ============================================================================
# Operator-Type Compatibility Matrix
# ============================================================================

# Maps operators to compatible data types
OPERATOR_TYPE_COMPATIBILITY: Final[dict[str, tuple[str, ...]]] = {
    OP_IS: (DATA_TYPE_TEXT, DATA_TYPE_NUMBER, DATA_TYPE_FLOAT, DATA_TYPE_CHECKBOX, DATA_TYPE_ENTITY, DATA_TYPE_DATE, DATA_TYPE_DATE_TIME, DATA_TYPE_STATUS_LIST, DATA_TYPE_LIST),
    OP_IS_NOT: (DATA_TYPE_TEXT, DATA_TYPE_NUMBER, DATA_TYPE_FLOAT, DATA_TYPE_CHECKBOX, DATA_TYPE_ENTITY, DATA_TYPE_DATE, DATA_TYPE_DATE_TIME, DATA_TYPE_STATUS_LIST, DATA_TYPE_LIST),
    OP_CONTAINS: (DATA_TYPE_TEXT, DATA_TYPE_LIST),
    OP_NOT_CONTAINS: (DATA_TYPE_TEXT, DATA_TYPE_LIST),
    OP_STARTS_WITH: (DATA_TYPE_TEXT,),
    OP_ENDS_WITH: (DATA_TYPE_TEXT,),
    OP_GREATER_THAN: (DATA_TYPE_NUMBER, DATA_TYPE_FLOAT, DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_LESS_THAN: (DATA_TYPE_NUMBER, DATA_TYPE_FLOAT, DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_BETWEEN: (DATA_TYPE_NUMBER, DATA_TYPE_FLOAT, DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_NOT_BETWEEN: (DATA_TYPE_NUMBER, DATA_TYPE_FLOAT, DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_IN: (DATA_TYPE_TEXT, DATA_TYPE_NUMBER, DATA_TYPE_ENTITY, DATA_TYPE_STATUS_LIST, DATA_TYPE_LIST),
    OP_NOT_IN: (DATA_TYPE_TEXT, DATA_TYPE_NUMBER, DATA_TYPE_ENTITY, DATA_TYPE_STATUS_LIST, DATA_TYPE_LIST),
    OP_IN_LAST: (DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_NOT_IN_LAST: (DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_IN_NEXT: (DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_NOT_IN_NEXT: (DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_IN_CALENDAR_DAY: (DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_IN_CALENDAR_WEEK: (DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_IN_CALENDAR_MONTH: (DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_IN_CALENDAR_YEAR: (DATA_TYPE_DATE, DATA_TYPE_DATE_TIME),
    OP_TYPE_IS: (DATA_TYPE_ENTITY, DATA_TYPE_MULTI_ENTITY),
    OP_TYPE_IS_NOT: (DATA_TYPE_ENTITY, DATA_TYPE_MULTI_ENTITY),
    OP_NAME_CONTAINS: (DATA_TYPE_ENTITY, DATA_TYPE_MULTI_ENTITY),
    OP_NAME_NOT_CONTAINS: (DATA_TYPE_ENTITY, DATA_TYPE_MULTI_ENTITY),
    OP_NAME_IS: (DATA_TYPE_ENTITY, DATA_TYPE_MULTI_ENTITY),
}

# ============================================================================
# Validation Configuration
# ============================================================================

# Default schema cache TTL (in seconds)
DEFAULT_SCHEMA_CACHE_TTL: Final[int] = 3600  # 1 hour

# Maximum number of suggestions to show in error messages
MAX_SUGGESTIONS: Final[int] = 10

# ============================================================================
# Filter Examples for Error Messages
# ============================================================================

# Example filters for different data types and operators
FILTER_EXAMPLES: Final[dict[str, dict[str, str]]] = {
    DATA_TYPE_TEXT: {
        OP_IS: 'query.filter({field}="example")',
        OP_IS_NOT: 'query.filter({field}__is_not="example")',
        OP_CONTAINS: 'query.filter({field}__contains="example")',
        OP_NOT_CONTAINS: 'query.filter({field}__not_contains="example")',
        OP_STARTS_WITH: 'query.filter({field}__starts_with="prefix")',
        OP_ENDS_WITH: 'query.filter({field}__ends_with="suffix")',
        OP_IN: 'query.filter({field}__in=["value1", "value2"])',
    },
    DATA_TYPE_NUMBER: {
        OP_IS: "query.filter({field}=123)",
        OP_IS_NOT: "query.filter({field}__is_not=123)",
        OP_GREATER_THAN: "query.filter({field}__greater_than=100)",
        OP_LESS_THAN: "query.filter({field}__less_than=1000)",
        OP_BETWEEN: "query.filter({field}__between=[10, 100])",
        OP_IN: "query.filter({field}__in=[1, 2, 3])",
    },
    DATA_TYPE_FLOAT: {
        OP_IS: "query.filter({field}=123.45)",
        OP_GREATER_THAN: "query.filter({field}__greater_than=100.0)",
        OP_LESS_THAN: "query.filter({field}__less_than=1000.0)",
        OP_BETWEEN: "query.filter({field}__between=[10.0, 100.0])",
    },
    DATA_TYPE_ENTITY: {
        OP_IS: 'query.filter({field}={{"type": "Project", "id": 123}})',
        OP_IS_NOT: 'query.filter({field}__is_not={{"type": "Project", "id": 123}})',
        OP_IN: 'query.filter({field}__in=[{{"type": "Project", "id": 1}}, {{"type": "Project", "id": 2}}])',
        OP_TYPE_IS: 'query.filter({field}__type_is="Asset")',
        OP_NAME_CONTAINS: 'query.filter({field}__name_contains="test")',
    },
    DATA_TYPE_MULTI_ENTITY: {
        OP_IS: 'query.filter({field}={{"type": "Asset", "id": 123}})',
        OP_IN: 'query.filter({field}__in=[{{"type": "Asset", "id": 1}}, {{"type": "Asset", "id": 2}}])',
        OP_TYPE_IS: 'query.filter({field}__type_is="Asset")',
        OP_NAME_CONTAINS: 'query.filter({field}__name_contains="test")',
    },
    DATA_TYPE_DATE: {
        OP_IS: 'query.filter({field}="2024-01-01")',
        OP_GREATER_THAN: 'query.filter({field}__greater_than="2024-01-01")',
        OP_LESS_THAN: 'query.filter({field}__less_than="2024-12-31")',
        OP_BETWEEN: 'query.filter({field}__between=["2024-01-01", "2024-12-31"])',
        OP_IN_LAST: 'query.filter({field}__in_last="7 days")',
        OP_IN_NEXT: 'query.filter({field}__in_next="30 days")',
    },
    DATA_TYPE_DATE_TIME: {
        OP_IS: 'query.filter({field}="2024-01-01 12:00:00")',
        OP_GREATER_THAN: 'query.filter({field}__greater_than="2024-01-01 00:00:00")',
        OP_IN_LAST: 'query.filter({field}__in_last="7 days")',
        OP_IN_NEXT: 'query.filter({field}__in_next="30 days")',
        OP_IN_CALENDAR_DAY: "query.filter({field}__in_calendar_day=None)",
        OP_IN_CALENDAR_WEEK: "query.filter({field}__in_calendar_week=None)",
    },
    DATA_TYPE_CHECKBOX: {
        OP_IS: "query.filter({field}=True)",
        OP_IS_NOT: "query.filter({field}__is_not=False)",
    },
    DATA_TYPE_STATUS_LIST: {
        OP_IS: 'query.filter({field}="ip")',
        OP_IS_NOT: 'query.filter({field}__is_not="na")',
        OP_IN: 'query.filter({field}__in=["ip", "fin", "wtg"])',
    },
    DATA_TYPE_LIST: {
        OP_CONTAINS: 'query.filter({field}__contains="value")',
        OP_NOT_CONTAINS: 'query.filter({field}__not_contains="value")',
    },
}

# Default example template
DEFAULT_FILTER_EXAMPLE: Final[str] = "query.filter({field}__{operator}=<value>)"


