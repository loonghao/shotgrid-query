"""Integration tests for QueryBuilder schema validation."""

from unittest.mock import MagicMock

import pytest

from shotgrid_query import Query, SchemaCache


class TestQueryBuilderValidation:
    """Tests for QueryBuilder validation integration."""

    def setup_method(self):
        """Clear schema cache before each test."""
        SchemaCache.clear()

    def test_query_without_schema_no_validation(self):
        """Test that query works without schema when not validating."""
        query = Query("Shot")
        query.filter(code="SHOT_010").select("code", "description")

        # Should work without schema
        filters = query.to_filters()
        fields = query.to_fields()

        assert len(filters) > 0
        assert len(fields) == 2

    def test_query_with_schema_manual_validation(self):
        """Test manual validation with provided schema."""
        schema = {
            "code": {"data_type": {"value": "text"}},
            "description": {"data_type": {"value": "text"}},
        }

        query = Query("Shot", schema=schema)
        query.filter(code="SHOT_010").select("code", "description")

        # Manual validation
        errors = query.validate()

        assert len(errors) == 0

    def test_query_with_schema_invalid_field(self):
        """Test validation catches invalid field."""
        schema = {"code": {"data_type": {"value": "text"}}}

        query = Query("Shot", schema=schema)
        query.filter(code="SHOT_010").select("invalid_field")

        errors = query.validate()

        assert len(errors) == 1
        assert errors[0].field == "invalid_field"
        assert "does not exist" in errors[0].message

    def test_query_with_schema_invalid_operator(self):
        """Test validation catches invalid operator."""
        schema = {"code": {"data_type": {"value": "text"}}}

        query = Query("Shot", schema=schema)
        query.filter_raw(("code", "greater_than", "value"))

        errors = query.validate()

        assert len(errors) == 1
        assert "not valid for field type" in errors[0].message

    def test_query_with_sg_connection(self):
        """Test validation with ShotGrid connection."""
        sg = MagicMock()
        sg.schema_field_read.return_value = {
            "code": {"data_type": {"value": "text"}},
            "description": {"data_type": {"value": "text"}},
        }

        query = Query("Shot", sg=sg)
        query.filter(code="SHOT_010").select("code", "description")

        errors = query.validate()

        assert len(errors) == 0
        assert sg.schema_field_read.call_count == 1

    def test_query_verify_parameter_true(self):
        """Test verify=True parameter raises on invalid query."""
        schema = {"code": {"data_type": {"value": "text"}}}

        query = Query("Shot", schema=schema)
        query.select("invalid_field")

        with pytest.raises(ValueError, match="validation failed"):
            query.to_fields(verify=True)

    def test_query_verify_parameter_false(self):
        """Test verify=False parameter doesn't validate."""
        schema = {"code": {"data_type": {"value": "text"}}}

        query = Query("Shot", schema=schema)
        query.select("invalid_field")

        # Should not raise
        fields = query.to_fields(verify=False)
        assert "invalid_field" in fields

    def test_query_auto_validate_true(self):
        """Test auto_validate=True validates automatically."""
        schema = {"code": {"data_type": {"value": "text"}}}

        query = Query("Shot", schema=schema, auto_validate=True)
        query.select("invalid_field")

        with pytest.raises(ValueError, match="validation failed"):
            query.to_fields()

    def test_query_auto_validate_false(self):
        """Test auto_validate=False doesn't validate automatically."""
        schema = {"code": {"data_type": {"value": "text"}}}

        query = Query("Shot", schema=schema, auto_validate=False)
        query.select("invalid_field")

        # Should not raise
        fields = query.to_fields()
        assert "invalid_field" in fields

    def test_query_verify_overrides_auto_validate(self):
        """Test that verify parameter overrides auto_validate setting."""
        schema = {"code": {"data_type": {"value": "text"}}}

        query = Query("Shot", schema=schema, auto_validate=True)
        query.select("invalid_field")

        # verify=False should override auto_validate=True
        fields = query.to_fields(verify=False)
        assert "invalid_field" in fields

    def test_query_without_schema_raises_on_validate(self):
        """Test that validate() raises when no schema available."""
        query = Query("Shot")
        query.filter(code="SHOT_010")

        errors = query.validate()

        assert len(errors) == 1
        assert "No schema available" in errors[0].message

    def test_query_schema_cache_reuse(self):
        """Test that schema cache is reused across queries."""
        sg = MagicMock()
        sg.schema_field_read.return_value = {"code": {"data_type": {"value": "text"}}}

        query1 = Query("Shot", sg=sg)
        query1.validate()

        query2 = Query("Shot", sg=sg)
        query2.validate()

        # Schema should only be fetched once
        assert sg.schema_field_read.call_count == 1

    def test_query_validation_with_filters_and_fields(self):
        """Test validation of both filters and fields."""
        schema = {
            "code": {"data_type": {"value": "text"}},
            "id": {"data_type": {"value": "number"}},
        }

        query = Query("Shot", schema=schema)
        query.filter(code="SHOT_010").filter(invalid_filter="value").select("code").select("invalid_field")

        errors = query.validate()

        # Should have 2 errors: invalid_filter and invalid_field
        assert len(errors) == 2
        error_fields = [e.field for e in errors]
        assert "invalid_filter" in error_fields
        assert "invalid_field" in error_fields
