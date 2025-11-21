"""Tests for data type utilities."""

import datetime

import pytest

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


class TestShotGridTypes:
    """Test ShotGridTypes constants."""

    def test_constants_exist(self):
        """Test that all expected constants exist."""
        assert ShotGridTypes.TEXT == "text"
        assert ShotGridTypes.NUMBER == "number"
        assert ShotGridTypes.FLOAT == "float"
        assert ShotGridTypes.DATE == "date"
        assert ShotGridTypes.DATE_TIME == "date_time"
        assert ShotGridTypes.ENTITY == "entity"
        assert ShotGridTypes.MULTI_ENTITY == "multi_entity"
        assert ShotGridTypes.CHECKBOX == "checkbox"
        assert ShotGridTypes.DURATION == "duration"
        assert ShotGridTypes.TIMECODE == "timecode"


class TestConvertToShotGridType:
    """Test convert_to_shotgrid_type function."""

    def test_convert_none(self):
        """Test converting None value."""
        result = convert_to_shotgrid_type(None, ShotGridTypes.TEXT)
        assert result is None

    def test_convert_date(self):
        """Test converting datetime to date."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 0)
        result = convert_to_shotgrid_type(dt, ShotGridTypes.DATE)
        assert result == "2024-01-15"

    def test_convert_datetime(self):
        """Test converting datetime."""
        dt = datetime.datetime(2024, 1, 15, 10, 30, 0)
        result = convert_to_shotgrid_type(dt, ShotGridTypes.DATE_TIME)
        assert result == dt

    def test_convert_checkbox(self):
        """Test converting to checkbox (bool)."""
        assert convert_to_shotgrid_type(1, ShotGridTypes.CHECKBOX) is True
        assert convert_to_shotgrid_type(0, ShotGridTypes.CHECKBOX) is False
        assert convert_to_shotgrid_type("yes", ShotGridTypes.CHECKBOX) is True

    def test_convert_number(self):
        """Test converting to number."""
        assert convert_to_shotgrid_type("123", ShotGridTypes.NUMBER) == 123
        assert convert_to_shotgrid_type(123.5, ShotGridTypes.NUMBER) == 123
        assert convert_to_shotgrid_type("invalid", ShotGridTypes.NUMBER) == "invalid"

    def test_convert_float(self):
        """Test converting to float."""
        assert convert_to_shotgrid_type("123.5", ShotGridTypes.FLOAT) == 123.5
        assert convert_to_shotgrid_type(123, ShotGridTypes.FLOAT) == 123.0
        assert convert_to_shotgrid_type("invalid", ShotGridTypes.FLOAT) == "invalid"

    def test_convert_entity(self):
        """Test converting entity value."""
        entity = {"type": "Project", "id": 123}
        result = convert_to_shotgrid_type(entity, ShotGridTypes.ENTITY)
        assert result == entity

        # Test with just an ID
        result = convert_to_shotgrid_type(123, ShotGridTypes.ENTITY)
        assert result == 123

    def test_convert_multi_entity(self):
        """Test converting multi-entity value."""
        entities = [{"type": "Project", "id": 123}, {"type": "Project", "id": 456}]
        result = convert_to_shotgrid_type(entities, ShotGridTypes.MULTI_ENTITY)
        assert result == entities

        # Test wrapping single entity in list
        entity = {"type": "Project", "id": 123}
        result = convert_to_shotgrid_type(entity, ShotGridTypes.MULTI_ENTITY)
        assert result == [entity]

    def test_convert_unknown_type(self):
        """Test converting unknown type returns as-is."""
        value = "test"
        result = convert_to_shotgrid_type(value, "unknown_type")
        assert result == value


class TestConvertFromShotGridType:
    """Test convert_from_shotgrid_type function."""

    def test_convert_none(self):
        """Test converting None value."""
        result = convert_from_shotgrid_type(None, ShotGridTypes.TEXT)
        assert result is None

    def test_convert_date_string(self):
        """Test converting date string to date object."""
        result = convert_from_shotgrid_type("2024-01-15", ShotGridTypes.DATE)
        assert isinstance(result, datetime.date)
        assert result == datetime.date(2024, 1, 15)

    def test_convert_invalid_date_string(self):
        """Test converting invalid date string."""
        result = convert_from_shotgrid_type("invalid", ShotGridTypes.DATE)
        assert result == "invalid"

    def test_convert_datetime_iso(self):
        """Test converting ISO datetime string."""
        result = convert_from_shotgrid_type("2024-01-15T10:30:00", ShotGridTypes.DATE_TIME)
        assert isinstance(result, datetime.datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_convert_datetime_standard(self):
        """Test converting standard datetime string."""
        result = convert_from_shotgrid_type("2024-01-15 10:30:00", ShotGridTypes.DATE_TIME)
        assert isinstance(result, datetime.datetime)

    def test_convert_duration(self):
        """Test converting duration (minutes to timedelta)."""
        result = convert_from_shotgrid_type(60, ShotGridTypes.DURATION)
        assert isinstance(result, datetime.timedelta)
        assert result == datetime.timedelta(minutes=60)

    def test_convert_timecode(self):
        """Test converting timecode (milliseconds to timedelta)."""
        result = convert_from_shotgrid_type(1000, ShotGridTypes.TIMECODE)
        assert isinstance(result, datetime.timedelta)
        assert result == datetime.timedelta(milliseconds=1000)

    def test_convert_unknown_type(self):
        """Test converting unknown type returns as-is."""
        value = "test"
        result = convert_from_shotgrid_type(value, "unknown_type")
        assert result == value


class TestFormatEntityValue:
    """Test format_entity_value function."""

    def test_format_entity_value(self):
        """Test formatting entity value."""
        result = format_entity_value("Project", 123)
        assert result == {"type": "Project", "id": 123}


class TestFormatMultiEntityValue:
    """Test format_multi_entity_value function."""

    def test_format_multi_entity_value(self):
        """Test formatting multi-entity value."""
        entities = [{"type": "Project", "id": 123}, {"type": "Asset", "id": 456}]
        result = format_multi_entity_value(entities)
        assert result == entities

    def test_format_empty_list(self):
        """Test formatting empty list."""
        result = format_multi_entity_value([])
        assert result == []


class TestSchemaFunctions:
    """Test schema-related functions."""

    def test_get_field_type(self):
        """Test getting field type from schema."""
        schema = {"Shot": {"fields": {"code": {"data_type": {"value": "text"}}}}}
        result = get_field_type(schema, "Shot", "code")
        assert result == "text"

    def test_get_field_type_missing_entity(self):
        """Test getting field type for missing entity."""
        schema = {}
        result = get_field_type(schema, "Shot", "code")
        assert result is None

    def test_get_field_type_missing_fields_key(self):
        """Test getting field type when fields key is missing."""
        schema = {"Shot": {}}
        result = get_field_type(schema, "Shot", "code")
        assert result is None

    def test_get_field_type_missing_field(self):
        """Test getting field type for missing field."""
        schema = {"Shot": {"fields": {}}}
        result = get_field_type(schema, "Shot", "code")
        assert result is None

    def test_is_entity_field(self):
        """Test checking if field is entity field."""
        schema = {"Shot": {"fields": {"project": {"data_type": {"value": "entity"}}}}}
        assert is_entity_field(schema, "Shot", "project") is True

        schema = {"Shot": {"fields": {"code": {"data_type": {"value": "text"}}}}}
        assert is_entity_field(schema, "Shot", "code") is False

    def test_is_multi_entity_field(self):
        """Test checking if field is multi-entity field."""
        schema = {"Shot": {"fields": {"assets": {"data_type": {"value": "multi_entity"}}}}}
        assert is_multi_entity_field(schema, "Shot", "assets") is True

        schema = {"Shot": {"fields": {"code": {"data_type": {"value": "text"}}}}}
        assert is_multi_entity_field(schema, "Shot", "code") is False

    def test_get_entity_field_types(self):
        """Test getting valid entity types for a field."""
        schema = {
            "Shot": {
                "fields": {
                    "entity": {
                        "data_type": {"value": "entity"},
                        "properties": {"valid_types": {"value": ["Asset", "Shot"]}},
                    }
                }
            }
        }
        result = get_entity_field_types(schema, "Shot", "entity")
        assert result == ["Asset", "Shot"]

    def test_get_entity_field_types_missing(self):
        """Test getting entity types when not available."""
        schema = {"Shot": {"fields": {"code": {"data_type": {"value": "text"}}}}}
        result = get_entity_field_types(schema, "Shot", "code")
        assert result == []

