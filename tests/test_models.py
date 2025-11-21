"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from shotgrid_query.models import (
    EntityRef,
    Filter,
    FilterOperator,
    FilterRequest,
    TimeFilter,
    TimeUnit,
)


class TestTimeUnit:
    """Test TimeUnit enum."""

    def test_time_unit_values(self):
        """Test TimeUnit enum values."""
        assert TimeUnit.DAY == "DAY"
        assert TimeUnit.WEEK == "WEEK"
        assert TimeUnit.MONTH == "MONTH"
        assert TimeUnit.YEAR == "YEAR"


class TestFilterOperator:
    """Test FilterOperator enum."""

    def test_filter_operator_values(self):
        """Test FilterOperator enum values."""
        assert FilterOperator.IS == "is"
        assert FilterOperator.IS_NOT == "is_not"
        assert FilterOperator.CONTAINS == "contains"
        assert FilterOperator.IN == "in"
        assert FilterOperator.BETWEEN == "between"


class TestEntityRef:
    """Test EntityRef model."""

    def test_create_entity_ref(self):
        """Test creating an EntityRef."""
        ref = EntityRef(type="Project", id=123)
        assert ref.type == "Project"
        assert ref.id == 123
        assert ref.name is None

    def test_create_entity_ref_with_name(self):
        """Test creating an EntityRef with name."""
        ref = EntityRef(type="Project", id=123, name="Test Project")
        assert ref.type == "Project"
        assert ref.id == 123
        assert ref.name == "Test Project"

    def test_entity_ref_allows_extra_fields(self):
        """Test that EntityRef allows extra fields."""
        ref = EntityRef(type="Project", id=123, code="PRJ001", custom_field="value")
        assert ref.type == "Project"
        assert ref.id == 123
        # Extra fields should be accessible
        assert ref.code == "PRJ001"  # type: ignore
        assert ref.custom_field == "value"  # type: ignore


class TestFilter:
    """Test Filter model."""

    def test_create_simple_filter(self):
        """Test creating a simple filter."""
        f = Filter(field="code", operator=FilterOperator.IS, value="SHOT001")
        assert f.field == "code"
        assert f.operator == FilterOperator.IS
        assert f.value == "SHOT001"

    def test_create_time_filter(self):
        """Test creating a time filter."""
        f = Filter(field="created_at", operator=FilterOperator.IN_LAST, value=[7, "DAY"])
        assert f.field == "created_at"
        assert f.operator == FilterOperator.IN_LAST
        assert f.value == [7, "DAY"]

    def test_filter_to_tuple(self):
        """Test converting filter to tuple."""
        f = Filter(field="code", operator=FilterOperator.IS, value="SHOT001")
        result = f.to_tuple()
        assert result == ("code", "is", "SHOT001")

    def test_filter_from_tuple(self):
        """Test creating filter from tuple."""
        f = Filter.from_tuple(("code", "is", "SHOT001"))
        assert f.field == "code"
        assert f.operator == FilterOperator.IS
        assert f.value == "SHOT001"

    def test_filter_validation_time_filter_dict(self):
        """Test that time filter value must be a dict."""
        with pytest.raises(ValidationError):
            Filter(field="created_at", operator=FilterOperator.IN_LAST, value="invalid")

    def test_filter_validation_between_list(self):
        """Test that between filter value must be a list."""
        with pytest.raises(ValidationError):
            Filter(field="id", operator=FilterOperator.BETWEEN, value="invalid")

    def test_filter_validation_between_two_elements(self):
        """Test that between filter value must have exactly 2 elements."""
        with pytest.raises(ValidationError):
            Filter(field="id", operator=FilterOperator.BETWEEN, value=[1, 2, 3])


class TestFilterRequest:
    """Test FilterRequest model."""

    def test_create_filter_request(self):
        """Test creating a FilterRequest."""
        req = FilterRequest(field="code", operator="is", value="SHOT001")
        assert req.field == "code"
        assert req.operator == "is"
        assert req.value == "SHOT001"

    def test_filter_request_from_dict(self):
        """Test creating FilterRequest from dict."""
        data = {"field": "code", "operator": "is", "value": "SHOT001"}
        req = FilterRequest.from_dict(data)
        assert req.field == "code"
        assert req.operator == "is"
        assert req.value == "SHOT001"

    def test_filter_request_from_dict_missing_fields(self):
        """Test creating FilterRequest from dict with missing fields."""
        data = {"field": "code", "operator": "is", "value": None}
        req = FilterRequest.from_dict(data)
        assert req.field == "code"
        assert req.operator == "is"
        assert req.value is None


class TestTimeFilter:
    """Test TimeFilter model."""

    def test_create_time_filter(self):
        """Test creating a TimeFilter."""
        tf = TimeFilter(field="created_at", operator="in_last", count=7, unit=TimeUnit.DAY)
        assert tf.field == "created_at"
        assert tf.operator == "in_last"
        assert tf.count == 7
        assert tf.unit == TimeUnit.DAY

    def test_time_filter_with_different_units(self):
        """Test TimeFilter with different units."""
        tf_week = TimeFilter(field="updated_at", operator="in_next", count=2, unit=TimeUnit.WEEK)
        assert tf_week.unit == TimeUnit.WEEK
        assert tf_week.count == 2

        tf_month = TimeFilter(field="created_at", operator="in_last", count=3, unit=TimeUnit.MONTH)
        assert tf_month.unit == TimeUnit.MONTH
        assert tf_month.count == 3

    def test_time_filter_to_filter(self):
        """Test converting TimeFilter to Filter."""
        tf = TimeFilter(field="created_at", operator="in_last", count=7, unit=TimeUnit.DAY)
        f = tf.to_filter()
        assert f.field == "created_at"
        assert f.operator == "in_last"  # type: ignore
        assert f.value == [7, "DAY"]

    def test_time_filter_validation_positive_count(self):
        """Test that count must be positive."""
        with pytest.raises(ValidationError):
            TimeFilter(field="created_at", operator="in_last", count=0, unit=TimeUnit.DAY)
