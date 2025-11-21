"""Tests for schema validation functionality."""

import time
from unittest.mock import MagicMock

from shotgrid_query.constants import (
    DATA_TYPE_DATE,
    DATA_TYPE_ENTITY,
    DATA_TYPE_NUMBER,
    DATA_TYPE_TEXT,
    DEFAULT_SCHEMA_CACHE_TTL,
    OP_CONTAINS,
    OP_GREATER_THAN,
    OP_IN_LAST,
    OP_IS,
)
from shotgrid_query.schema_validator import (
    SchemaCache,
    ValidationError,
    _get_filter_example,
    get_operator_suggestion,
    is_operator_valid_for_type,
    validate_field_exists,
    validate_fields,
    validate_filter_value_type,
    validate_filters,
)


class TestSchemaCache:
    """Tests for SchemaCache class."""

    def setup_method(self):
        """Clear cache before each test."""
        SchemaCache.clear()

    def test_cache_stores_schema(self):
        """Test that schema is cached correctly."""
        sg = MagicMock()
        sg.schema_field_read.return_value = {"code": {"data_type": {"value": "text"}}}

        schema = SchemaCache.get(sg, "Shot")

        assert schema == {"code": {"data_type": {"value": "text"}}}
        assert sg.schema_field_read.call_count == 1

    def test_cache_returns_cached_schema(self):
        """Test that cached schema is returned without API call."""
        sg = MagicMock()
        sg.schema_field_read.return_value = {"code": {"data_type": {"value": "text"}}}

        # First call
        schema1 = SchemaCache.get(sg, "Shot")
        # Second call
        schema2 = SchemaCache.get(sg, "Shot")

        assert schema1 == schema2
        assert sg.schema_field_read.call_count == 1  # Only called once

    def test_cache_respects_ttl(self):
        """Test that cache expires after TTL."""
        sg = MagicMock()
        sg.schema_field_read.return_value = {"code": {"data_type": {"value": "text"}}}

        # Set very short TTL
        SchemaCache.set_ttl(1)

        # First call
        SchemaCache.get(sg, "Shot")

        # Wait for TTL to expire
        time.sleep(1.1)

        # Second call should fetch again
        SchemaCache.get(sg, "Shot")

        assert sg.schema_field_read.call_count == 2

        # Reset TTL
        SchemaCache.set_ttl(DEFAULT_SCHEMA_CACHE_TTL)

    def test_cache_different_entity_types(self):
        """Test that different entity types are cached separately."""
        sg = MagicMock()
        sg.schema_field_read.side_effect = [
            {"code": {"data_type": {"value": "text"}}},
            {"name": {"data_type": {"value": "text"}}},
        ]

        schema1 = SchemaCache.get(sg, "Shot")
        schema2 = SchemaCache.get(sg, "Asset")

        assert schema1 != schema2
        assert sg.schema_field_read.call_count == 2

    def test_cache_clear(self):
        """Test that cache can be cleared."""
        sg = MagicMock()
        sg.schema_field_read.return_value = {"code": {"data_type": {"value": "text"}}}

        # Cache schema
        SchemaCache.get(sg, "Shot")

        # Clear cache
        SchemaCache.clear()

        # Should fetch again
        SchemaCache.get(sg, "Shot")

        assert sg.schema_field_read.call_count == 2


class TestValidationError:
    """Tests for ValidationError class."""

    def test_validation_error_creation(self):
        """Test creating a ValidationError."""
        error = ValidationError(field="code", message="Field does not exist", suggestion="Use 'name' instead")

        assert error.field == "code"
        assert error.message == "Field does not exist"
        assert error.suggestion == "Use 'name' instead"

    def test_validation_error_str(self):
        """Test string representation of ValidationError."""
        error = ValidationError(field="code", message="Field does not exist", suggestion="Use 'name' instead")

        error_str = str(error)
        assert "code" in error_str
        assert "Field does not exist" in error_str
        assert "Use 'name' instead" in error_str

    def test_validation_error_without_suggestion(self):
        """Test ValidationError without suggestion."""
        error = ValidationError(field="code", message="Field does not exist")

        assert error.field == "code"
        assert error.message == "Field does not exist"
        assert error.suggestion is None


class TestOperatorValidation:
    """Tests for operator validation functions."""

    def test_is_operator_valid_for_type_valid(self):
        """Test valid operator-type combinations."""
        assert is_operator_valid_for_type(OP_IS, DATA_TYPE_TEXT) is True
        assert is_operator_valid_for_type(OP_CONTAINS, DATA_TYPE_TEXT) is True
        assert is_operator_valid_for_type(OP_GREATER_THAN, DATA_TYPE_NUMBER) is True
        assert is_operator_valid_for_type(OP_IN_LAST, DATA_TYPE_DATE) is True

    def test_is_operator_valid_for_type_invalid(self):
        """Test invalid operator-type combinations."""
        assert is_operator_valid_for_type(OP_CONTAINS, DATA_TYPE_NUMBER) is False
        assert is_operator_valid_for_type(OP_GREATER_THAN, DATA_TYPE_TEXT) is False
        assert is_operator_valid_for_type(OP_IN_LAST, DATA_TYPE_TEXT) is False

    def test_is_operator_valid_for_unknown_operator(self):
        """Test that unknown operators are considered valid (let ShotGrid handle it)."""
        assert is_operator_valid_for_type("unknown_operator", DATA_TYPE_TEXT) is True

    def test_get_operator_suggestion(self):
        """Test getting operator suggestions for a field type."""
        suggestions = get_operator_suggestion(DATA_TYPE_TEXT)
        assert OP_IS in suggestions
        assert OP_CONTAINS in suggestions
        assert OP_GREATER_THAN not in suggestions

    def test_get_operator_suggestion_for_number(self):
        """Test getting operator suggestions for number fields."""
        suggestions = get_operator_suggestion(DATA_TYPE_NUMBER)
        assert OP_IS in suggestions
        assert OP_GREATER_THAN in suggestions
        assert OP_CONTAINS not in suggestions


class TestValueTypeValidation:
    """Tests for value type validation."""

    def test_validate_entity_value_valid(self):
        """Test valid entity value."""
        field_info = {
            "data_type": {"value": DATA_TYPE_ENTITY},
            "properties": {"valid_types": {"value": ["Project", "Asset"]}},
        }
        value = {"type": "Project", "id": 123}

        is_valid, error = validate_filter_value_type(value, field_info, OP_IS)

        assert is_valid is True
        assert error is None

    def test_validate_entity_value_invalid_format(self):
        """Test invalid entity value format."""
        field_info = {"data_type": {"value": DATA_TYPE_ENTITY}}
        value = "invalid"

        is_valid, error = validate_filter_value_type(value, field_info, OP_IS)

        assert is_valid is False
        assert "dict with 'type' and 'id' keys" in error

    def test_validate_entity_value_invalid_type(self):
        """Test entity value with invalid entity type."""
        field_info = {
            "data_type": {"value": DATA_TYPE_ENTITY},
            "properties": {"valid_types": {"value": ["Project"]}},
        }
        value = {"type": "Asset", "id": 123}

        is_valid, error = validate_filter_value_type(value, field_info, OP_IS)

        assert is_valid is False
        assert "not valid" in error
        assert "Project" in error

    def test_validate_number_value_valid(self):
        """Test valid number value."""
        field_info = {"data_type": {"value": DATA_TYPE_NUMBER}}
        value = 123

        is_valid, error = validate_filter_value_type(value, field_info, OP_IS)

        assert is_valid is True
        assert error is None

    def test_validate_number_value_invalid(self):
        """Test invalid number value."""
        field_info = {"data_type": {"value": DATA_TYPE_NUMBER}}
        value = "not a number"

        is_valid, error = validate_filter_value_type(value, field_info, OP_IS)

        assert is_valid is False
        assert "must be a number" in error

    def test_validate_text_value_valid(self):
        """Test valid text value."""
        field_info = {"data_type": {"value": DATA_TYPE_TEXT}}
        value = "test"

        is_valid, error = validate_filter_value_type(value, field_info, OP_IS)

        assert is_valid is True
        assert error is None

    def test_validate_text_value_invalid(self):
        """Test invalid text value."""
        field_info = {"data_type": {"value": DATA_TYPE_TEXT}}
        value = 123

        is_valid, error = validate_filter_value_type(value, field_info, OP_IS)

        assert is_valid is False
        assert "must be a string" in error

    def test_validate_none_value(self):
        """Test that None values are always valid."""
        field_info = {"data_type": {"value": DATA_TYPE_TEXT}}
        value = None

        is_valid, error = validate_filter_value_type(value, field_info, OP_IS)

        assert is_valid is True
        assert error is None


class TestFieldValidation:
    """Tests for field validation."""

    def test_validate_field_exists_valid(self):
        """Test validating an existing field."""
        schema = {"code": {"data_type": {"value": DATA_TYPE_TEXT}}}

        error = validate_field_exists("code", schema, "Shot")

        assert error is None

    def test_validate_field_exists_invalid(self):
        """Test validating a non-existent field."""
        schema = {"code": {"data_type": {"value": DATA_TYPE_TEXT}}}

        error = validate_field_exists("invalid_field", schema, "Shot")

        assert error is not None
        assert error.field == "invalid_field"
        assert "does not exist" in error.message
        assert "Available fields" in error.suggestion

    def test_validate_field_exists_related_field(self):
        """Test validating a related field."""
        schema = {"project": {"data_type": {"value": DATA_TYPE_ENTITY}}}

        error = validate_field_exists("project.Project.name", schema, "Shot")

        assert error is None  # Base field exists

    def test_validate_fields_all_valid(self):
        """Test validating multiple valid fields."""
        schema = {
            "code": {"data_type": {"value": DATA_TYPE_TEXT}},
            "description": {"data_type": {"value": DATA_TYPE_TEXT}},
        }
        fields = ["code", "description"]

        errors = validate_fields(fields, schema, "Shot")

        assert len(errors) == 0

    def test_validate_fields_some_invalid(self):
        """Test validating fields with some invalid."""
        schema = {"code": {"data_type": {"value": DATA_TYPE_TEXT}}}
        fields = ["code", "invalid_field"]

        errors = validate_fields(fields, schema, "Shot")

        assert len(errors) == 1
        assert errors[0].field == "invalid_field"


class TestFilterValidation:
    """Tests for filter validation."""

    def test_validate_filters_all_valid(self):
        """Test validating all valid filters."""
        schema = {
            "code": {"data_type": {"value": DATA_TYPE_TEXT}},
            "id": {"data_type": {"value": DATA_TYPE_NUMBER}},
        }
        filters = [
            ("code", OP_IS, "SHOT_010"),
            ("id", OP_GREATER_THAN, 100),
        ]

        errors = validate_filters(filters, schema, "Shot")

        assert len(errors) == 0

    def test_validate_filters_invalid_field(self):
        """Test validating filters with invalid field."""
        schema = {"code": {"data_type": {"value": DATA_TYPE_TEXT}}}
        filters = [("invalid_field", OP_IS, "value")]

        errors = validate_filters(filters, schema, "Shot")

        assert len(errors) == 1
        assert errors[0].field == "invalid_field"
        assert "does not exist" in errors[0].message

    def test_validate_filters_invalid_operator(self):
        """Test validating filters with invalid operator for field type."""
        schema = {"code": {"data_type": {"value": DATA_TYPE_TEXT}}}
        filters = [("code", OP_GREATER_THAN, "value")]

        errors = validate_filters(filters, schema, "Shot")

        assert len(errors) == 1
        assert errors[0].field == "code"
        assert "not valid for field type" in errors[0].message
        assert "Valid operators" in errors[0].suggestion

    def test_validate_filters_invalid_value_type(self):
        """Test validating filters with invalid value type."""
        schema = {"id": {"data_type": {"value": DATA_TYPE_NUMBER}}}
        filters = [("id", OP_IS, "not a number")]

        errors = validate_filters(filters, schema, "Shot")

        assert len(errors) == 1
        assert errors[0].field == "id"
        assert "Example:" in errors[0].suggestion

    def test_validate_filters_multiple_errors(self):
        """Test validating filters with multiple errors."""
        schema = {"code": {"data_type": {"value": DATA_TYPE_TEXT}}}
        filters = [
            ("invalid_field", OP_IS, "value"),
            ("code", OP_GREATER_THAN, "value"),
        ]

        errors = validate_filters(filters, schema, "Shot")

        assert len(errors) == 2


class TestFilterExamples:
    """Tests for filter example generation."""

    def test_get_filter_example_text(self):
        """Test getting example for text field."""
        example = _get_filter_example("code", OP_IS, DATA_TYPE_TEXT)

        assert "code" in example
        assert "query.filter" in example

    def test_get_filter_example_number(self):
        """Test getting example for number field."""
        example = _get_filter_example("id", OP_GREATER_THAN, DATA_TYPE_NUMBER)

        assert "id" in example
        assert "query.filter" in example
        assert "greater_than" in example

    def test_get_filter_example_entity(self):
        """Test getting example for entity field."""
        example = _get_filter_example("project", OP_IS, DATA_TYPE_ENTITY)

        assert "project" in example
        assert "type" in example
        assert "id" in example

    def test_get_filter_example_unknown_type(self):
        """Test getting example for unknown field type."""
        example = _get_filter_example("field", "unknown_op", "unknown_type")

        assert "field" in example
        assert "unknown_op" in example
