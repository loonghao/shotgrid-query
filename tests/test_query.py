"""Tests for QueryBuilder."""

from unittest.mock import MagicMock, Mock

import pytest

from shotgrid_query.query import Query, QueryBuilder


class TestQueryBuilder:
    """Test QueryBuilder class."""

    def test_init(self):
        """Test QueryBuilder initialization."""
        query = QueryBuilder("Shot")
        assert query._entity_type == "Shot"
        assert query._filters == []
        assert query._fields == []
        assert query._limit is None

    def test_filter_simple(self):
        """Test adding simple filter."""
        query = QueryBuilder("Shot").filter(code="SHOT_010")
        filters = query.to_filters()
        assert ("code", "is", "SHOT_010") in filters

    def test_filter_multiple_kwargs(self):
        """Test adding multiple filters at once."""
        query = QueryBuilder("Shot").filter(code="SHOT_010", sg_status_list="ip")
        filters = query.to_filters()
        assert len(filters) == 2

    def test_filter_with_operator(self):
        """Test filter with operator suffix."""
        query = QueryBuilder("Shot").filter(code__contains="SHOT")
        filters = query.to_filters()
        assert ("code", "contains", "SHOT") in filters

    def test_filter_in_operator(self):
        """Test filter with 'in' operator."""
        query = QueryBuilder("Shot").filter(sg_status_list__in=["ip", "fin"])
        filters = query.to_filters()
        assert ("sg_status_list", "in", ["ip", "fin"]) in filters

    def test_filter_time_operator(self):
        """Test filter with time operator."""
        query = QueryBuilder("Shot").filter(created_at__in_last="7 days")
        filters = query.to_filters()
        # Should be processed to [7, "DAY"]
        assert len(filters) == 1
        assert filters[0][0] == "created_at"
        assert filters[0][1] == "in_last"
        assert filters[0][2] == [7, "DAY"]

    def test_filter_chaining(self):
        """Test chaining multiple filter calls."""
        query = QueryBuilder("Shot").filter(code="SHOT_010").filter(sg_status_list="ip")
        filters = query.to_filters()
        assert len(filters) == 2

    def test_filter_raw(self):
        """Test adding raw filters."""
        query = QueryBuilder("Shot").filter_raw(("code", "is", "SHOT_010"), ("sg_status_list", "in", ["ip", "fin"]))
        filters = query.to_filters()
        assert len(filters) == 2

    def test_select(self):
        """Test selecting fields."""
        query = QueryBuilder("Shot").select("code", "description")
        fields = query.to_fields()
        assert "code" in fields
        assert "description" in fields

    def test_select_chaining(self):
        """Test chaining select calls."""
        query = QueryBuilder("Shot").select("code").select("description", "sg_status_list")
        fields = query.to_fields()
        assert len(fields) == 3

    def test_select_related(self):
        """Test selecting related fields."""
        query = QueryBuilder("Shot").select_related("project", ["name", "code"])
        fields = query.to_fields()
        assert "project.name" in fields
        assert "project.code" in fields

    def test_order_by_ascending(self):
        """Test ordering by field ascending."""
        query = QueryBuilder("Shot").order_by("code")
        query_dict = query.to_dict()
        assert query_dict["order"] == [{"field_name": "code", "direction": "asc"}]

    def test_order_by_descending(self):
        """Test ordering by field descending."""
        query = QueryBuilder("Shot").order_by("-created_at")
        query_dict = query.to_dict()
        assert query_dict["order"] == [{"field_name": "created_at", "direction": "desc"}]

    def test_order_by_multiple(self):
        """Test ordering by multiple fields."""
        query = QueryBuilder("Shot").order_by("project", "-code")
        query_dict = query.to_dict()
        assert len(query_dict["order"]) == 2

    def test_limit(self):
        """Test setting limit."""
        query = QueryBuilder("Shot").limit(100)
        assert query._limit == 100
        query_dict = query.to_dict()
        assert query_dict["limit"] == 100

    def test_retired_only(self):
        """Test retired_only flag."""
        query = QueryBuilder("Shot").retired_only()
        assert query._retired_only is True
        query_dict = query.to_dict()
        assert query_dict["retired_only"] is True

    def test_include_archived_projects(self):
        """Test include_archived_projects flag."""
        query = QueryBuilder("Shot").include_archived_projects(False)
        assert query._include_archived_projects is False
        query_dict = query.to_dict()
        assert query_dict["include_archived_projects"] is False

    def test_filter_operator_any(self):
        """Test setting filter operator to 'any' (OR)."""
        query = QueryBuilder("Shot").filter_operator("any")
        assert query._filter_operator == "any"
        query_dict = query.to_dict()
        assert query_dict["filter_operator"] == "any"

    def test_filter_operator_invalid(self):
        """Test setting invalid filter operator raises error."""
        query = QueryBuilder("Shot")
        with pytest.raises(ValueError, match="Invalid filter operator"):
            query.filter_operator("invalid")

    def test_to_dict(self):
        """Test converting query to dictionary."""
        query = (
            QueryBuilder("Shot")
            .filter(code="SHOT_010")
            .select("code", "description")
            .order_by("-created_at")
            .limit(100)
        )
        query_dict = query.to_dict()

        assert query_dict["entity_type"] == "Shot"
        assert "filters" in query_dict
        assert "fields" in query_dict
        assert "order" in query_dict
        assert query_dict["limit"] == 100

    def test_execute(self):
        """Test executing query with mock ShotGrid connection."""
        # Create mock ShotGrid connection
        mock_sg = Mock()
        mock_sg.find = MagicMock(
            return_value=[
                {"type": "Shot", "id": 1, "code": "SHOT_010"},
                {"type": "Shot", "id": 2, "code": "SHOT_020"},
            ]
        )

        query = QueryBuilder("Shot").filter(sg_status_list="ip").select("code", "description").limit(10)

        results = query.execute(mock_sg)

        # Verify sg.find was called
        mock_sg.find.assert_called_once()
        call_args = mock_sg.find.call_args

        # Check arguments
        assert call_args[0][0] == "Shot"  # entity_type
        assert len(call_args[0][1]) > 0  # filters
        assert call_args[0][2] == ["code", "description"]  # fields

        # Check results
        assert len(results) == 2
        assert results[0]["code"] == "SHOT_010"

    def test_first(self):
        """Test getting first result."""
        mock_sg = Mock()
        mock_sg.find = MagicMock(
            return_value=[
                {"type": "Shot", "id": 1, "code": "SHOT_010"},
            ]
        )

        query = QueryBuilder("Shot").filter(code="SHOT_010")
        result = query.first(mock_sg)

        assert result is not None
        assert result["code"] == "SHOT_010"

        # Verify limit was set to 1
        call_args = mock_sg.find.call_args
        assert call_args[1]["limit"] == 1

    def test_first_no_results(self):
        """Test getting first result when no results."""
        mock_sg = Mock()
        mock_sg.find = MagicMock(return_value=[])

        query = QueryBuilder("Shot").filter(code="NONEXISTENT")
        result = query.first(mock_sg)

        assert result is None

    def test_clone(self):
        """Test cloning a query."""
        original = QueryBuilder("Shot").filter(code="SHOT_010").select("code", "description").limit(100)

        cloned = original.clone()

        # Verify they are different objects
        assert cloned is not original
        assert cloned._filters is not original._filters
        assert cloned._fields is not original._fields

        # Verify they have the same configuration
        assert cloned._entity_type == original._entity_type
        assert cloned._filters == original._filters
        assert cloned._fields == original._fields
        assert cloned._limit == original._limit

        # Verify modifying clone doesn't affect original
        cloned.filter(sg_status_list="ip")
        assert len(cloned._filters) == len(original._filters) + 1

    def test_repr(self):
        """Test string representation."""
        query = QueryBuilder("Shot").filter(code="SHOT_010").select("code").limit(10)
        repr_str = repr(query)

        assert "QueryBuilder" in repr_str
        assert "Shot" in repr_str
        assert "filters=1" in repr_str
        assert "fields=1" in repr_str
        assert "limit=10" in repr_str

    def test_query_alias(self):
        """Test that Query is an alias for QueryBuilder."""
        assert Query is QueryBuilder
