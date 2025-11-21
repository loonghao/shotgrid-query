"""ShotGrid Query Builder - A Pythonic query builder for ShotGrid/Flow Production Tracking API.

This library provides a type-safe, chainable query builder and ORM-like abstraction
layer for the ShotGrid API, making it easier to construct complex queries with
better developer experience.

Example:
    >>> from shotgrid_query import Query, FilterBuilder
    >>> query = Query("Shot").filter(sg_status_list="ip").select("code", "description")
    >>> filters = query.to_filters()
"""

__version__ = "0.1.0"

# Import core components
from shotgrid_query.custom_types import (
    ASSET_ENTITY_TYPE,
    GROUP_ENTITY_TYPE,
    HUMAN_USER_ENTITY_TYPE,
    NOTE_ENTITY_TYPE,
    PLAYLIST_ENTITY_TYPE,
    PROJECT_ENTITY_TYPE,
    PUBLISHED_FILE_ENTITY_TYPE,
    SHOT_ENTITY_TYPE,
    TASK_ENTITY_TYPE,
    VERSION_ENTITY_TYPE,
    Entity,
    EntityRef,
    EntityType,
    Filter,
    FilterOperator,
    LocalUrlField,
    ShotGridDataType,
    ShotGridValue,
    UrlField,
)
from shotgrid_query.data_types import (
    ShotGridTypes,
    convert_from_shotgrid_type,
    convert_to_shotgrid_type,
    format_entity_value,
    format_multi_entity_value,
    get_entity_field_types,
    get_field_type,
    is_entity_field,
    is_multi_entity_field,
)
from shotgrid_query.filters import (
    FilterBuilder,
    TimeUnit,
    build_date_filter,
    combine_filters,
    create_date_filter,
    process_filters,
    validate_filters,
)
from shotgrid_query.models import (
    EntityRef as EntityRefModel,
    Filter as FilterModel,
    FilterOperator as FilterOperatorEnum,
    FilterRequest,
    TimeFilter,
    TimeUnit as TimeUnitEnum,
)
from shotgrid_query.query import Query, QueryBuilder
from shotgrid_query.field_mapper import FieldMapper
from shotgrid_query.adapters import BaseAdapter

# Try to import optional adapters
try:
    from shotgrid_query.adapters import PythonAPIAdapter
    _has_python_api = True
except ImportError:
    _has_python_api = False

# Public API exports
__all__ = [
    "__version__",
    # Custom types
    "EntityType",
    "EntityRef",
    "Entity",
    "Filter",
    "FilterOperator",
    "ShotGridDataType",
    "ShotGridValue",
    "UrlField",
    "LocalUrlField",
    # Entity type constants
    "PROJECT_ENTITY_TYPE",
    "SHOT_ENTITY_TYPE",
    "ASSET_ENTITY_TYPE",
    "TASK_ENTITY_TYPE",
    "VERSION_ENTITY_TYPE",
    "NOTE_ENTITY_TYPE",
    "PLAYLIST_ENTITY_TYPE",
    "HUMAN_USER_ENTITY_TYPE",
    "GROUP_ENTITY_TYPE",
    "PUBLISHED_FILE_ENTITY_TYPE",
    # Data types
    "ShotGridTypes",
    "convert_to_shotgrid_type",
    "convert_from_shotgrid_type",
    "get_field_type",
    "is_entity_field",
    "is_multi_entity_field",
    "get_entity_field_types",
    "format_entity_value",
    "format_multi_entity_value",
    # Filters
    "FilterBuilder",
    "TimeUnit",
    "process_filters",
    "validate_filters",
    "create_date_filter",
    "build_date_filter",
    "combine_filters",
    # Models
    "EntityRefModel",
    "FilterModel",
    "FilterOperatorEnum",
    "FilterRequest",
    "TimeFilter",
    "TimeUnitEnum",
    # Query Builder
    "Query",
    "QueryBuilder",
    # Field Mapper
    "FieldMapper",
    # Adapters
    "BaseAdapter",
]

# Add PythonAPIAdapter to __all__ if available
if _has_python_api:
    from shotgrid_query.adapters import PythonAPIAdapter
    __all__.append("PythonAPIAdapter")

