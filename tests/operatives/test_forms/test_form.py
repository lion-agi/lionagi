import pytest
from pydantic import Field

from lionagi.operatives.forms.form import Form
from lionagi.utils import UNDEFINED


class SimpleTaskForm(Form):
    """A simple task form for testing."""

    input_value: str = Field(default=UNDEFINED)
    output_value: str = Field(default=UNDEFINED)
    optional_value: str | None = Field(default=None)


def test_form_initialization():
    """Test basic initialization of Form."""
    form = Form(assignment="input -> output")
    assert form.assignment == "input -> output"
    assert not form.strict_form
    assert form.guidance is None
    assert isinstance(form.init_input_kwargs, dict)


def test_form_with_strict():
    """Test Form with strict_form=True."""
    form = Form(
        assignment="input -> output",
        strict_form=True,
    )
    assert form.strict_form

    # Test modifying assignment in strict mode
    with pytest.raises(ValueError, match="Cannot modify"):
        form.assignment = "new -> assignment"


def test_check_input_output_list_omitted():
    """Test input/output field validation during initialization."""
    # Test valid assignment
    form = Form(assignment="input1, input2 -> output1, output2")
    assert form.input_fields == ["input1", "input2"]
    assert form.request_fields == ["output1", "output2"]

    # Test invalid cases
    with pytest.raises(ValueError):
        Form(input_fields=["field1"])  # Explicit input fields not allowed

    with pytest.raises(ValueError):
        Form(request_fields=["field1"])  # Explicit request fields not allowed

    with pytest.raises(ValueError):
        Form()  # Missing assignment


def test_check_input_output_fields():
    """Test input/output field validation after initialization."""
    form = SimpleTaskForm(assignment="input_value -> output_value")
    assert "input_value" in form.input_fields
    assert "output_value" in form.request_fields
    assert form.input_value is UNDEFINED


def test_work_fields():
    """Test work_fields property."""
    form = SimpleTaskForm(assignment="input_value -> output_value")
    assert set(form.work_fields) == {"input_value", "output_value"}


def test_required_fields():
    """Test required_fields property."""
    form = SimpleTaskForm(
        assignment="input_value -> output_value",
        output_fields=["optional_value"],
    )
    assert set(form.required_fields) == {
        "input_value",
        "output_value",
        "optional_value",
    }


def test_validation_kwargs():
    """Test validation_kwargs property."""
    form = SimpleTaskForm(assignment="input_value -> output_value")
    assert isinstance(form.validation_kwargs, dict)
    assert "input_value" in form.validation_kwargs
    assert "output_value" in form.validation_kwargs


def test_instruction_dict():
    """Test instruction_dict and related properties."""
    form = SimpleTaskForm(
        assignment="input_value -> output_value",
        guidance="Test guidance",
    )

    instruction_dict = form.instruction_dict
    assert "context" in instruction_dict
    assert "instruction" in instruction_dict
    assert "request_fields" in instruction_dict

    # Test instruction content
    assert "input_value" in instruction_dict["context"]
    assert "guidance" in instruction_dict["instruction"]
    assert "output_value" in instruction_dict["request_fields"]


def test_fill_input_fields():
    """Test fill_input_fields method."""
    # Test with none_as_valid_value=False (default)
    form1 = SimpleTaskForm(assignment="input_value -> output_value")
    form2 = SimpleTaskForm(assignment="input_value -> output_value")

    # Initial state should be UNDEFINED
    assert form1.input_value is UNDEFINED
    assert form2.input_value is UNDEFINED

    # Fill form2 with a value
    form2.input_value = "source_input"

    # Fill form1 from form2 (should work since form1.input_value is UNDEFINED)
    form1.fill_input_fields(form=form2)
    assert form1.input_value == "source_input"

    # Try to fill again with kwargs (should not override since value exists)
    form1.fill_input_fields(input_value="new_input")
    assert form1.input_value == "source_input"  # Value should not change

    # Test with none_as_valid_value=True
    form3 = SimpleTaskForm(
        assignment="input_value -> output_value",
        none_as_valid_value=True,
    )
    form3.input_value = None
    form3.fill_input_fields(input_value="new_input")
    assert form3.input_value is None  # Should not change from None


def test_fill_request_fields():
    """Test fill_request_fields method."""
    # Test with none_as_valid_value=False (default)
    form1 = SimpleTaskForm(assignment="input_value -> output_value")
    form2 = SimpleTaskForm(assignment="input_value -> output_value")

    # Initial state should be UNDEFINED
    assert form1.output_value is UNDEFINED
    assert form2.output_value is UNDEFINED

    # Fill form2 with a value
    form2.output_value = "source_result"

    # Fill form1 from form2 (should work since form1.output_value is UNDEFINED)
    form1.fill_request_fields(form=form2)
    assert form1.output_value == "source_result"

    # Try to fill again with kwargs (should not override since value exists)
    form1.fill_request_fields(output_value="result")
    assert form1.output_value == "source_result"  # Value should not change

    # Test with none_as_valid_value=True
    form3 = SimpleTaskForm(
        assignment="input_value -> output_value",
        none_as_valid_value=True,
    )
    form3.output_value = None
    form3.fill_request_fields(output_value="result")
    assert form3.output_value is None  # Should not change from None


def test_from_form():
    """Test from_form class method."""
    source_form = SimpleTaskForm(
        assignment="input_value -> output_value",
        guidance="Test guidance",
    )
    source_form.input_value = "test_input"

    # Test creating new form from source
    new_form = SimpleTaskForm.from_form(
        form=source_form,
        fill_inputs=True,
    )
    assert new_form.input_value == "test_input"
    assert new_form.guidance == "Test guidance"

    # Test with fill_inputs=False
    new_form = SimpleTaskForm.from_form(
        form=source_form,
        fill_inputs=False,
    )
    assert new_form.input_value is UNDEFINED


def test_remove_request_from_output():
    """Test remove_request_from_output method."""
    form = SimpleTaskForm(
        assignment="input_value -> output_value",
        output_fields=["input_value", "output_value"],
    )

    form.remove_request_from_output()
    assert "output_value" not in form.output_fields
    assert "input_value" in form.output_fields


def test_append_methods():
    """Test append_to_input, append_to_output, and append_to_request methods."""
    form = SimpleTaskForm(assignment="input_value -> output_value")

    # Test append_to_input
    form.append_to_input("new_input", value="test")
    assert "new_input" in form.input_fields
    assert form.new_input == "test"

    # Test append_to_output
    form.append_to_output("new_output")
    assert "new_output" in form.output_fields

    # Test append_to_request
    form.append_to_request("new_request")
    assert "new_request" in form.request_fields

    # Test append_to_request with value (should raise error)
    with pytest.raises(ValueError):
        form.append_to_request("invalid", value="test")


def test_strict_form_modifications():
    """Test modifications in strict form mode."""
    form = SimpleTaskForm(
        assignment="input_value -> output_value",
        strict_form=True,
    )

    # Test modifying fields in strict mode
    with pytest.raises(ValueError):
        form.append_to_input("new_input")

    with pytest.raises(ValueError):
        form.append_to_request("new_request")


def test_none_as_valid_value():
    """Test none_as_valid_value behavior."""
    form = SimpleTaskForm(
        assignment="input_value -> output_value",
        none_as_valid_value=True,
    )

    # Test filling with None
    form.fill_input_fields(input_value=None)
    assert form.input_value is None
    assert form.is_workable()  # None should be valid

    # Test with none_as_valid_value=False
    form = SimpleTaskForm(
        assignment="input_value -> output_value",
        none_as_valid_value=False,
    )
    form.fill_input_fields(input_value=None)
    assert not form.is_workable()  # None should not be valid
