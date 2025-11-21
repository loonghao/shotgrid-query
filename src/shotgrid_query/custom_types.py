"""Type definitions for ShotGrid query builder.

This module provides type definitions for ShotGrid API data types.
"""

import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict, Union

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
    name: Optional[str]


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

    local_path: Optional[str]
    local_path_linux: Optional[str]
    local_path_mac: Optional[str]
    local_path_windows: Optional[str]
    local_storage: Dict[str, Any]


# ShotGrid filter
Filter = Tuple[str, FilterOperator, Any]

# ShotGrid value types
ShotGridValue = Union[
    None,
    bool,
    int,
    float,
    str,
    datetime.datetime,
    datetime.date,
    Dict[str, Any],
    List[Dict[str, Any]],
    List[str],
]


# ShotGrid entity
class Entity(TypedDict, total=False):
    """ShotGrid entity."""

    type: str
    id: int
    name: Optional[str]
    code: Optional[str]
    project: Optional[EntityRef]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    created_by: Optional[EntityRef]
    updated_by: Optional[EntityRef]
    sg_status_list: Optional[str]
    description: Optional[str]
    image: Optional[str]
    tags: Optional[List[EntityRef]]

