"""Type definitions for ShotGrid query builder.

This module provides type definitions for ShotGrid API data types.
"""

import datetime
from typing import Any, Literal, TypedDict

# ShotGrid entity types
EntityType = str  # Use string type instead of Literal for flexibility

# Common entity type constants
PROJECT_ENTITY_TYPE = "Project"
SHOT_ENTITY_TYPE = "Shot"
ASSET_ENTITY_TYPE = "Asset"
TASK_ENTITY_TYPE = "Task"
VERSION_ENTITY_TYPE = "Version"
NOTE_ENTITY_TYPE = "Note"
PLAYLIST_ENTITY_TYPE = "Playlist"
HUMAN_USER_ENTITY_TYPE = "HumanUser"
GROUP_ENTITY_TYPE = "Group"
PUBLISHED_FILE_ENTITY_TYPE = "PublishedFile"

# ShotGrid data types
ShotGridDataType = Literal[
    "addressing",
    "checkbox",
    "color",
    "currency",
    "date",
    "date_time",
    "duration",
    "entity",
    "float",
    "footage",
    "image",
    "list",
    "multi_entity",
    "number",
    "password",
    "percent",
    "serializable",
    "status_list",
    "system_task_type",
    "tag_list",
    "text",
    "timecode",
    "url",
]

# ShotGrid filter operators
FilterOperator = Literal[
    "is",
    "is_not",
    "less_than",
    "greater_than",
    "contains",
    "not_contains",
    "starts_with",
    "ends_with",
    "between",
    "not_between",
    "in",
    "not_in",
    "in_last",
    "not_in_last",
    "in_next",
    "not_in_next",
    "in_calendar_day",
    "in_calendar_week",
    "in_calendar_month",
    "in_calendar_year",
    "name_contains",
    "name_not_contains",
    "name_is",
    "type_is",
    "type_is_not",
]


# ShotGrid entity reference
class EntityRef(TypedDict):
    """ShotGrid entity reference."""

    type: str
    id: int
    name: str | None


# ShotGrid URL field
class UrlField(TypedDict):
    """ShotGrid URL field."""

    content_type: str
    link_type: Literal["local", "url", "upload"]
    name: str
    url: str


# ShotGrid local file URL field
class LocalUrlField(UrlField):
    """ShotGrid local file URL field."""

    local_path: str | None
    local_path_linux: str | None
    local_path_mac: str | None
    local_path_windows: str | None
    local_storage: dict[str, Any]


# ShotGrid filter
# Using str instead of FilterOperator for better compatibility
Filter = tuple[str, str, Any]

# ShotGrid value types
ShotGridValue = (
    None
    | bool
    | int
    | float
    | str
    | datetime.datetime
    | datetime.date
    | dict[str, Any]
    | list[dict[str, Any]]
    | list[str]
)


# ShotGrid entity
class Entity(TypedDict, total=False):
    """ShotGrid entity."""

    type: str
    id: int
    name: str | None
    code: str | None
    project: EntityRef | None
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None
    created_by: EntityRef | None
    updated_by: EntityRef | None
    sg_status_list: str | None
    description: str | None
    image: str | None
    tags: list[EntityRef] | None
