"""Tests for FieldMapper."""

from shotgrid_query.field_mapper import FieldMapper


class TestFieldMapper:
    """Test FieldMapper class."""

    def test_init_without_schema(self):
        """Test initialization without schema."""
        mapper = FieldMapper("Shot")
        assert mapper._entity_type == "Shot"
        assert mapper._schema == {}
        assert mapper._field_cache == {}

    def test_init_with_schema(self):
        """Test initialization with schema."""
        schema = {"Shot": {"project": {"data_type": {"value": "entity"}}}}
        mapper = FieldMapper("Shot", schema)
        assert mapper._entity_type == "Shot"
        assert mapper._schema == schema

    def test_resolve_simple_field(self):
        """Test resolving a simple field."""
        mapper = FieldMapper("Shot")
        result = mapper.resolve_field("code")
        assert result == "code"

    def test_resolve_field_caching(self):
        """Test that field resolution is cached."""
        mapper = FieldMapper("Shot")
        result1 = mapper.resolve_field("code")
        result2 = mapper.resolve_field("code")
        assert result1 == result2
        assert "code" in mapper._field_cache

    def test_resolve_already_resolved_field(self):
        """Test resolving a field that's already in ShotGrid format."""
        mapper = FieldMapper("Shot")
        result = mapper.resolve_field("project.Project.name")
        assert result == "project.Project.name"

    def test_resolve_field_with_schema(self):
        """Test resolving a field with schema information."""
        schema = {
            "Shot": {
                "project": {
                    "data_type": {"value": "entity"},
                    "properties": {"valid_types": {"value": ["Project"]}},
                }
            }
        }
        mapper = FieldMapper("Shot", schema)
        result = mapper.resolve_field("project.name")
        assert result == "project.Project.name"

    def test_resolve_field_without_schema(self):
        """Test resolving a field without schema (should return as-is with warning)."""
        mapper = FieldMapper("Shot")
        result = mapper.resolve_field("project.name")
        # Without schema, it should return as-is
        assert result == "project.name"

    def test_resolve_field_with_multiple_valid_types(self):
        """Test resolving a field with multiple valid entity types."""
        schema = {
            "Shot": {
                "entity": {
                    "data_type": {"value": "entity"},
                    "properties": {"valid_types": {"value": ["Asset", "Shot"]}},
                }
            }
        }
        mapper = FieldMapper("Shot", schema)
        result = mapper.resolve_field("entity.name")
        # Should return as-is when multiple types are possible
        assert result == "entity.name"

    def test_resolve_field_with_long_path(self):
        """Test resolving a field with more than 3 parts."""
        mapper = FieldMapper("Shot")
        result = mapper.resolve_field("a.b.c.d")
        # Should return as-is for unsupported formats
        assert result == "a.b.c.d"

    def test_resolve_fields_multiple(self):
        """Test resolving multiple fields."""
        schema = {
            "Shot": {
                "project": {
                    "data_type": {"value": "entity"},
                    "properties": {"valid_types": {"value": ["Project"]}},
                }
            }
        }
        mapper = FieldMapper("Shot", schema)
        fields = ["code", "project.name", "description"]
        result = mapper.resolve_fields(fields)
        assert result == ["code", "project.Project.name", "description"]

    def test_get_related_fields_with_schema(self):
        """Test getting related fields with schema."""
        schema = {
            "Shot": {
                "project": {
                    "data_type": {"value": "entity"},
                    "properties": {"valid_types": {"value": ["Project"]}},
                }
            }
        }
        mapper = FieldMapper("Shot", schema)
        result = mapper.get_related_fields("project", ["name", "code"])
        assert result == ["project.Project.name", "project.Project.code"]

    def test_get_related_fields_without_schema(self):
        """Test getting related fields without schema (fallback)."""
        mapper = FieldMapper("Shot")
        result = mapper.get_related_fields("project", ["name", "code"])
        # Should use simplified format as fallback
        assert result == ["project.name", "project.code"]

    def test_clear_cache(self):
        """Test clearing the field cache."""
        mapper = FieldMapper("Shot")
        mapper.resolve_field("code")
        mapper.resolve_field("name")
        assert len(mapper._field_cache) == 2

        mapper.clear_cache()
        assert len(mapper._field_cache) == 0

    def test_get_related_entity_type_no_schema(self):
        """Test getting related entity type without schema."""
        mapper = FieldMapper("Shot")
        result = mapper._get_related_entity_type("project")
        assert result is None

    def test_get_related_entity_type_with_schema(self):
        """Test getting related entity type with schema."""
        schema = {
            "Shot": {
                "project": {
                    "data_type": {"value": "entity"},
                    "properties": {"valid_types": {"value": ["Project"]}},
                }
            }
        }
        mapper = FieldMapper("Shot", schema)
        result = mapper._get_related_entity_type("project")
        assert result == "Project"

    def test_get_related_entity_type_non_entity_field(self):
        """Test getting related entity type for non-entity field."""
        schema = {"Shot": {"code": {"data_type": {"value": "text"}}}}
        mapper = FieldMapper("Shot", schema)
        result = mapper._get_related_entity_type("code")
        assert result is None
