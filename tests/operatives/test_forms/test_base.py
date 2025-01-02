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
    form = BaseForm(template_name="test_form")
    assert form.template_name == "test_form"
    assert form.output_fields == []
    assert not form.none_as_valid_value
    assert not form.has_processed


def test_base_form_with_output_fields():
    """Test BaseForm with output fields."""
    form = BaseForm(
        template_name="test_form",
        output_fields=["field1", "field2"],
    )
    assert form.output_fields == ["field1", "field2"]


def test_check_is_completed():
    """Test check_is_completed method."""
    # Test with none_as_valid_value=False
    form = SimpleForm(
        output_fields=["field1", "field2", "field3"],
        none_as_valid_value=False,
    )
    missing = form.check_is_completed(handle_how="return_missing")
    assert set(missing) == {
        "field2",
        "field3",
    }  # None and UNDEFINED are invalid

    # Test with none_as_valid_value=True
    form = SimpleForm(
        output_fields=["field1", "field2", "field3"],
        none_as_valid_value=True,
    )
    missing = form.check_is_completed(handle_how="return_missing")
    assert missing == ["field3"]  # Only UNDEFINED is invalid

    # Test with all fields filled
    form.field3 = "value3"
    assert form.check_is_completed(handle_how="return_missing") is None
    assert form.has_processed


def test_check_is_completed_raises():
    """Test check_is_completed raises ValueError."""
    form = SimpleForm(
        output_fields=["field1", "field3"],
        none_as_valid_value=False,
    )
    with pytest.raises(ValueError, match="Incomplete request fields"):
        form.check_is_completed(handle_how="raise")


def test_is_completed():
    """Test is_completed method."""
    # Test with none_as_valid_value=True
    form = SimpleForm(
        output_fields=["field1", "field2"],
        none_as_valid_value=True,
    )
    assert form.is_completed()  # field1 has default, field2 is None (valid)

    # Test with none_as_valid_value=False
    form = SimpleForm(
        output_fields=["field1", "field2"],
        none_as_valid_value=False,
    )
    assert not form.is_completed()  # field2 is None (invalid)

    form.field2 = 42
    assert form.is_completed()  # Now all fields are valid


def test_validate_output():
    """Test _validate_output validator."""
    # Test with string
    form = BaseForm(output_fields="field1")
    assert form.output_fields == ["field1"]

    # Test with list
    form = BaseForm(output_fields=["field1", "field2"])
    assert form.output_fields == ["field1", "field2"]

    # Test with empty value
    form = BaseForm(output_fields=[])
    assert form.output_fields == []


def test_work_fields():
    """Test work_fields property."""
    form = SimpleForm(output_fields=["field1", "field2"])
    assert form.work_fields == ["field1", "field2"]


def test_work_dict():
    """Test work_dict property."""
    form = SimpleForm(output_fields=["field1", "field2"])
    expected = {
        "field1": "default1",
        "field2": None,
    }
    assert form.work_dict == expected


def test_required_fields():
    """Test required_fields property."""
    form = SimpleForm(output_fields=["field1", "field2"])
    assert form.required_fields == ["field1", "field2"]


def test_required_dict():
    """Test required_dict property."""
    form = SimpleForm(output_fields=["field1", "field2"])
    expected = {
        "field1": "default1",
        "field2": None,
    }
    assert form.required_dict == expected


def test_get_results():
    """Test get_results method."""
    form = SimpleForm(
        output_fields=["field1", "field2", "field3"],
        none_as_valid_value=True,
    )

    # Test with suppress=True
    results = form.get_results(suppress=True)
    assert results["field1"] == "default1"
    assert results["field2"] is None
    assert results["field3"] is UNDEFINED

    # Test with valid_only=True and none_as_valid_value=True
    results = form.get_results(valid_only=True)
    assert results["field1"] == "default1"
    assert results["field2"] is None  # None is valid
    assert "field3" not in results  # UNDEFINED is filtered out

    # Test with valid_only=True and none_as_valid_value=False
    form.none_as_valid_value = False
    results = form.get_results(valid_only=True)
    assert results["field1"] == "default1"
    assert "field2" not in results  # None is filtered out
    assert "field3" not in results  # UNDEFINED is filtered out


def test_get_results_raises():
    """Test get_results raises ValueError."""
    form = SimpleForm(output_fields=["nonexistent_field"])
    with pytest.raises(ValueError, match="Missing field"):
        form.get_results(suppress=False)


def test_display_dict():
    """Test display_dict property."""
    form = SimpleForm(output_fields=["field1", "field2"])
    expected = {
        "field1": "default1",
        "field2": None,
    }
    assert form.display_dict == expected


def test_none_as_valid_value():
    """Test none_as_valid_value behavior."""
    # Test with none_as_valid_value=True
    form = SimpleForm(
        output_fields=["field1", "field2"],
        none_as_valid_value=True,
    )
    assert form.is_completed()  # None is valid

    # Test with none_as_valid_value=False
    form = SimpleForm(
        output_fields=["field1", "field2"],
        none_as_valid_value=False,
    )
    assert not form.is_completed()  # None is invalid
    missing = form.check_is_completed(handle_how="return_missing")
    assert "field2" in missing


def test_assignment():
    """Test assignment field."""
    form = SimpleForm(
        assignment="input1, input2 -> output",
        output_fields=["field1"],
    )
    assert form.assignment == "input1, input2 -> output"


def test_invalid_output_fields():
    """Test invalid output_fields validation."""
    with pytest.raises(ValueError, match="Invalid output fields"):
        BaseForm(output_fields=123)
