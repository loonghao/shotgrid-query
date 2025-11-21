"""Tests for filter building and validation."""

from datetime import datetime, timedelta

import pytest

from shotgrid_query.filters import (
    FilterBuilder,
    build_date_filter,
    combine_filters,
    process_filters,
    validate_filters,
)


class TestFilterBuilder:
    """Test FilterBuilder static methods."""

    def test_is_field(self):
        """Test creating 'is' filter."""
        result = FilterBuilder.is_field("code", "SHOT_010")
        assert result == ("code", "is", "SHOT_010")

    def test_is_not_field(self):
        """Test creating 'is_not' filter."""
        result = FilterBuilder.is_not_field("code", "SHOT_010")
        assert result == ("code", "is_not", "SHOT_010")

    def test_contains(self):
        """Test creating 'contains' filter."""
        result = FilterBuilder.contains("description", "test")
        assert result == ("description", "contains", "test")

    def test_not_contains(self):
        """Test creating 'not_contains' filter."""
        result = FilterBuilder.not_contains("description", "test")
        assert result == ("description", "not_contains", "test")

    def test_starts_with(self):
        """Test creating 'starts_with' filter."""
        result = FilterBuilder.starts_with("code", "SHOT")
        assert result == ("code", "starts_with", "SHOT")

    def test_ends_with(self):
        """Test creating 'ends_with' filter."""
        result = FilterBuilder.ends_with("code", "010")
        assert result == ("code", "ends_with", "010")

    def test_greater_than(self):
        """Test creating 'greater_than' filter."""
        result = FilterBuilder.greater_than("id", 100)
        assert result == ("id", "greater_than", 100)

    def test_less_than(self):
        """Test creating 'less_than' filter."""
        result = FilterBuilder.less_than("id", 100)
        assert result == ("id", "less_than", 100)

    def test_between(self):
        """Test creating 'between' filter."""
        result = FilterBuilder.between("id", 100, 200)
        assert result == ("id", "between", [100, 200])

    def test_in_list(self):
        """Test creating 'in' filter."""
        result = FilterBuilder.in_list("sg_status_list", ["ip", "fin"])
        assert result == ("sg_status_list", "in", ["ip", "fin"])

    def test_not_in_list(self):
        """Test creating 'not_in' filter."""
        result = FilterBuilder.not_in_list("sg_status_list", ["hld", "omt"])
        assert result == ("sg_status_list", "not_in", ["hld", "omt"])

    def test_in_last(self):
        """Test creating 'in_last' filter."""
        result = FilterBuilder.in_last("created_at", 7, "DAY")
        assert result == ("created_at", "in_last", [7, "DAY"])

    def test_in_next(self):
        """Test creating 'in_next' filter."""
        result = FilterBuilder.in_next("due_date", 30, "DAY")
        assert result == ("due_date", "in_next", [30, "DAY"])

    def test_in_calendar_day(self):
        """Test creating 'in_calendar_day' filter."""
        result = FilterBuilder.in_calendar_day("created_at")
        assert result == ("created_at", "in_calendar_day", None)

    def test_type_is(self):
        """Test creating 'type_is' filter."""
        result = FilterBuilder.type_is("entity", "Shot")
        assert result == ("entity", "type_is", "Shot")

    def test_name_contains(self):
        """Test creating 'name_contains' filter."""
        result = FilterBuilder.name_contains("project", "Demo")
        assert result == ("project", "name_contains", "Demo")

    def test_today(self):
        """Test creating today filter."""
        result = FilterBuilder.today("created_at")
        expected_date = datetime.now().strftime("%Y-%m-%d")
        assert result == ("created_at", "is", expected_date)

    def test_in_project(self):
        """Test creating project filter."""
        result = FilterBuilder.in_project(123)
        assert result == ("project", "is", {"type": "Project", "id": 123})

    def test_by_user(self):
        """Test creating user filter."""
        result = FilterBuilder.by_user(456)
        assert result == ("created_by", "is", {"type": "HumanUser", "id": 456})

    def test_assigned_to(self):
        """Test creating assigned_to filter."""
        result = FilterBuilder.assigned_to(789)
        assert result == ("task_assignees", "is", {"type": "HumanUser", "id": 789})


class TestValidateFilters:
    """Test filter validation."""

    def test_valid_simple_filter(self):
        """Test validating a simple valid filter."""
        filters = [("code", "is", "SHOT_010")]
        errors = validate_filters(filters)
        assert errors == []

    def test_valid_multiple_filters(self):
        """Test validating multiple valid filters."""
        filters = [
            ("code", "is", "SHOT_010"),
            ("sg_status_list", "in", ["ip", "fin"]),
            ("created_at", "in_last", [7, "DAY"]),
        ]
        errors = validate_filters(filters)
        assert errors == []

    def test_invalid_filter_structure(self):
        """Test validating filter with invalid structure."""
        filters = [("code", "is")]  # Missing value
        errors = validate_filters(filters)
        assert len(errors) > 0
        assert "must be a list/tuple with exactly 3 elements" in errors[0]

    def test_invalid_operator(self):
        """Test validating filter with invalid operator."""
        filters = [("code", "invalid_op", "SHOT_010")]
        errors = validate_filters(filters)
        assert len(errors) > 0
        assert "Invalid operator" in errors[0]

    def test_invalid_time_filter_value(self):
        """Test validating time filter with invalid value."""
        filters = [("created_at", "in_last", "invalid")]
        errors = validate_filters(filters)
        assert len(errors) > 0

    def test_invalid_between_filter_value(self):
        """Test validating between filter with invalid value."""
        filters = [("id", "between", 100)]  # Should be [min, max]
        errors = validate_filters(filters)
        assert len(errors) > 0
        assert "must be a list with exactly 2 elements" in errors[0]


class TestProcessFilters:
    """Test filter processing."""

    def test_process_simple_filters(self):
        """Test processing simple filters."""
        filters = [("code", "is", "SHOT_010")]
        result = process_filters(filters)
        assert result == [("code", "is", "SHOT_010")]

    def test_process_time_filter_string(self):
        """Test processing time filter with string value."""
        filters = [("created_at", "in_last", "7 days")]
        result = process_filters(filters)
        assert result == [("created_at", "in_last", [7, "DAY"])]

    def test_process_time_filter_weeks(self):
        """Test processing time filter with weeks."""
        filters = [("created_at", "in_last", "2 weeks")]
        result = process_filters(filters)
        assert result == [("created_at", "in_last", [2, "WEEK"])]

    def test_process_time_filter_months(self):
        """Test processing time filter with months."""
        filters = [("created_at", "in_last", "3 months")]
        result = process_filters(filters)
        assert result == [("created_at", "in_last", [3, "MONTH"])]

    def test_process_time_filter_already_formatted(self):
        """Test processing time filter already in correct format."""
        filters = [("created_at", "in_last", [7, "DAY"])]
        result = process_filters(filters)
        assert result == [("created_at", "in_last", [7, "DAY"])]

    def test_process_invalid_filters_raises(self):
        """Test that processing invalid filters raises ValueError."""
        filters = [("code", "invalid_op", "SHOT_010")]
        with pytest.raises(ValueError, match="Invalid filters"):
            process_filters(filters)


class TestBuildDateFilter:
    """Test date filter building."""

    def test_build_date_filter_with_datetime(self):
        """Test building date filter with datetime object."""
        dt = datetime(2023, 1, 15, 10, 30)
        result = build_date_filter("created_at", "is", dt)
        assert result == ("created_at", "is", "2023-01-15")

    def test_build_date_filter_with_timedelta(self):
        """Test building date filter with timedelta."""
        td = timedelta(days=7)
        result = build_date_filter("created_at", "greater_than", td)
        expected_date = (datetime.now() + td).strftime("%Y-%m-%d")
        assert result == ("created_at", "greater_than", expected_date)

    def test_build_date_filter_with_string(self):
        """Test building date filter with string."""
        result = build_date_filter("created_at", "is", "2023-01-15")
        assert result == ("created_at", "is", "2023-01-15")

    def test_build_date_filter_with_none(self):
        """Test building date filter with None (defaults to today)."""
        result = build_date_filter("created_at", "is", None)
        expected_date = datetime.now().strftime("%Y-%m-%d")
        assert result == ("created_at", "is", expected_date)


class TestCombineFilters:
    """Test filter combination."""

    def test_combine_filters_and(self):
        """Test combining filters with AND operator."""
        filters = [
            ("code", "is", "SHOT_010"),
            ("sg_status_list", "is", "ip"),
        ]
        result = combine_filters(filters, "and")
        assert result["filter_operator"] == "and"
        assert len(result["filters"]) == 2

    def test_combine_filters_or(self):
        """Test combining filters with OR operator."""
        filters = [
            ("code", "is", "SHOT_010"),
            ("code", "is", "SHOT_020"),
        ]
        result = combine_filters(filters, "or")
        assert result["filter_operator"] == "or"
        assert len(result["filters"]) == 2

    def test_combine_filters_invalid_operator(self):
        """Test combining filters with invalid operator."""
        filters = [("code", "is", "SHOT_010")]
        with pytest.raises(ValueError, match="Invalid filter operator"):
            combine_filters(filters, "invalid")
