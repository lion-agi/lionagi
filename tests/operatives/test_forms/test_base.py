import pytest
from pydantic import Field

from lionagi.operatives.forms.base import BaseForm
from lionagi.utils import UNDEFINED


class SimpleForm(BaseForm):
    """A simple form class for testing."""

    field1: str = Field(default="default1")
    field2: int | None = Field(default=None)
    field3: str = Field(default=UNDEFINED)


def test_base_form_initialization():
    """Test basic initialization of BaseForm."""
    form = BaseForm()
    assert form.assignment is None
    assert form.output_fields == []
    assert not form.none_as_valid
    assert not form.has_processed


def test_base_form_with_output_fields():
    """Test BaseForm with output fields."""
    form = BaseForm(
        output_fields=["field1", "field2"],
    )
    assert form.output_fields == ["field1", "field2"]


def test_check_completeness():
    """Test check_completeness method."""
    # Test with none_as_valid=False
    form = SimpleForm(
        output_fields=["field1", "field2", "field3"],
        none_as_valid=False,
    )
    missing = form.check_completeness()
    assert set(missing) == {
        "field2",
        "field3",
    }  # None and UNDEFINED are invalid

    # Test with none_as_valid=True
    form = SimpleForm(
        output_fields=["field1", "field2", "field3"],
        none_as_valid=True,
    )
    missing = form.check_completeness()
    assert missing == ["field3"]  # Only UNDEFINED is invalid

    # Test with all fields filled
    form.field3 = "value3"
    assert not form.check_completeness()


def test_check_completeness_raises():
    """Test check_completeness raises ValueError."""
    form = SimpleForm(
        output_fields=["field1", "field3"],
        none_as_valid=False,
    )
    with pytest.raises(ValueError, match="Form missing required fields"):
        form.check_completeness(how="raise")


def test_is_completed():
    """Test is_completed method."""
    # Test with none_as_valid=True
    form = SimpleForm(
        output_fields=["field1", "field2"],
        none_as_valid=True,
    )
    assert form.is_completed()  # field1 has default, field2 is None (valid)

    # Test with none_as_valid=False
    form = SimpleForm(
        output_fields=["field1", "field2"],
        none_as_valid=False,
    )
    assert not form.is_completed()  # field2 is None (invalid)

    form.field2 = 42
    assert form.is_completed()  # Now all fields are valid


def test_get_results():
    """Test get_results method."""
    form = SimpleForm(
        output_fields=["field1", "field2", "field3"],
        none_as_valid=True,
    )

    # Test with valid_only=False (default)
    results = form.get_results()
    assert results["field1"] == "default1"
    assert results["field2"] is None
    assert results["field3"] is UNDEFINED

    # Test with valid_only=True and none_as_valid=True
    results = form.get_results(valid_only=True)
    assert results["field1"] == "default1"
    assert results["field2"] is None  # None is valid
    assert "field3" not in results  # UNDEFINED is filtered out

    # Test with valid_only=True and none_as_valid=False
    form.none_as_valid = False
    results = form.get_results(valid_only=True)
    assert results["field1"] == "default1"
    assert "field2" not in results  # None is filtered out
    assert "field3" not in results  # UNDEFINED is filtered out


def test_assignment():
    """Test assignment field."""
    form = SimpleForm(
        assignment="input1, input2 -> output",
        output_fields=["field1"],
    )
    assert form.assignment == "input1, input2 -> output"
