from typing import Any

import pytest
from lionabc.exceptions import (
    LionOperationError,
    LionTypeError,
    LionValueError,
)
from lionfuncs import LN_UNDEFINED, LionUndefinedType
from pydantic import Field
from pydantic_core import PydanticUndefined

from lion_core.form.base import BaseForm
from lion_core.form.form import Form
from lion_core.generic.component import Component
from lion_core.generic.note import Note


# Helper functions and classes
def create_sample_form(**kwargs):
    class SampleForm(Form):
        field1: str | None | Any = Field(default=None)
        field2: int | None | Any = Field(default=None)

    return SampleForm(**kwargs)


# Test Form initialization and basic properties
def test_form_init():
    form = Form(assignment="field1, field2 -> field3")
    assert form.assignment == "field1, field2 -> field3"
    assert form.input_fields == ["field1", "field2"]
    assert form.request_fields == ["field3"]
    assert not form.strict_form
    assert form.guidance is None

    form_with_fields = create_sample_form(
        assignment="field1 -> field2",
        guidance="Test guidance",
        task_description="Test description",
    )
    assert form_with_fields.guidance == "Test guidance"
    assert form_with_fields.task_description == "Test description"


def test_form_input_output_validation():
    with pytest.raises(ValueError):
        Form(assignment="-> output")  # Missing input

    with pytest.raises(ValueError):
        Form(assignment="input ->")  # Missing output

    with pytest.raises(ValueError):
        Form(
            assignment="field1 -> field2", input_fields=["field1"]
        )  # Explicit input not allowed

    with pytest.raises(ValueError):
        Form(
            assignment="field1 -> field2", request_fields=["field2"]
        )  # Explicit request not allowed

    with pytest.raises(ValueError):
        Form(
            assignment="field1 -> field2", task="Custom task"
        )  # Explicit task not allowed


# Test Form properties
def test_form_work_fields():
    form = create_sample_form(assignment="field1 -> field2")
    assert form.work_fields == ["field1", "field2"]


def test_form_required_fields():
    form = create_sample_form(
        assignment="field1 -> field2", output_fields=["field3"]
    )
    assert set(form.required_fields) == {"field1", "field2", "field3"}


def test_form_validation_kwargs():
    form = create_sample_form(assignment="field1 -> field2")
    assert form.validation_kwargs == {"field1": {}, "field2": {}}


def test_form_instruction_dict():
    form = create_sample_form(assignment="field1 -> field2")
    instruction_dict = form.instruction_dict
    assert "context" in instruction_dict
    assert "instruction" in instruction_dict
    assert "request_fields" in instruction_dict


# Test Form methods
def test_form_check_is_completed():
    form = create_sample_form(assignment="field1 -> field2")
    form.field1 = "value1"
    form.field2 = 42

    assert form.check_is_completed() is None
    assert form.has_processed

    form.field2 = LN_UNDEFINED
    with pytest.raises(LionOperationError):
        form.check_is_completed()

    missing = form.check_is_completed(handle_how="return_missing")
    assert missing == ["field2"]


def test_form_check_is_workable():
    form = create_sample_form(assignment="field1 -> field2")

    with pytest.raises(LionOperationError):
        form.check_is_workable()

    form.field1 = "value1"
    assert form.check_is_workable() is None

    form.field1 = None
    missing = form.check_is_workable(handle_how="return_missing")
    assert missing == ["field1"]


def test_form_is_completed():
    form = create_sample_form(assignment="field1 -> field2")
    assert not form.is_completed()

    form.field1 = "value1"
    form.field2 = 42
    assert form.is_completed()


def test_form_is_workable():
    form = create_sample_form(assignment="field1 -> field2")
    assert not form.is_workable()

    form.field1 = "value1"
    assert form.is_workable()


def test_form_to_dict():
    form = create_sample_form(assignment="field1 -> field2")
    form.field1 = "value1"
    form_dict = form.to_dict()
    assert "field1" in form_dict
    assert "field2" in form_dict

    form_dict_valid = form.to_dict(valid_only=True)
    assert "field1" in form_dict_valid
    assert "field2" not in form_dict_valid


def test_form_from_dict():
    data = {
        "assignment": "field1 -> field2",
        "field1": "value1",
        "extra_field": "extra_value",
    }
    form = Form.from_dict(data)
    assert form.assignment == "field1 -> field2"
    assert form.field1 == "value1"
    assert form.extra_field == "extra_value"


def test_form_fill_input_fields():
    form1 = create_sample_form(assignment="field1 -> field2")
    form2 = create_sample_form(assignment="field1 -> field2", field1="value1")

    form1.fill_input_fields(form2)
    assert form1.field1 == "value1"

    form1.field1 = LN_UNDEFINED
    form1.fill_input_fields(field1="new_value")
    assert form1.field1 == "new_value"


def test_form_fill_request_fields():
    form1 = create_sample_form(assignment="field1 -> field2")
    form2 = create_sample_form(assignment="field1 -> field2", field2=42)

    form1.fill_request_fields(form2)
    assert form1.field2 == 42

    form1.field2 = LN_UNDEFINED
    form1.fill_request_fields(field2=84)
    assert form1.field2 == 84


def test_form_from_form():
    form1 = create_sample_form(assignment="field1 -> field2", field1="value1")
    form2 = Form.from_form(form1)

    assert form2.assignment == "field1 -> field2"
    assert form2.field1 == "value1"

    # Test with form class
    FormClass = create_sample_form(assignment="field1 -> field2").__class__
    form3 = Form.from_form(
        FormClass, assignment="field1 -> field2", field1="new_value"
    )
    assert form3.field1 == "new_value"


def test_form_remove_request_from_output():
    form = create_sample_form(
        assignment="field1 -> field2", output_fields=["field1", "field2"]
    )
    form.remove_request_from_output()
    assert form.output_fields == ["field1"]


def test_form_append_operations():
    form = create_sample_form(assignment="field1 -> field2")

    form.append_to_input("new_input", value="new_value")
    assert "new_input" in form.input_fields
    assert form.new_input == "new_value"
    assert "new_input" in form.assignment

    form.append_to_output("new_output")
    assert "new_output" in form.output_fields

    form.append_to_request("new_request")
    assert "new_request" in form.request_fields
    assert "new_request" in form.assignment

    with pytest.raises(LionValueError):
        form.append_to_request("invalid_request", value="invalid")


# Test error handling
def test_form_error_handling():
    with pytest.raises(ValueError):
        Form(assignment="invalid assignment")

    form = create_sample_form(assignment="field1 -> field2")
    with pytest.raises(LionTypeError):
        form.fill_input_fields("not a form")

    with pytest.raises(LionTypeError):
        Form.from_form("not a form")


# Test with LN_UNDEFINED and PydanticUndefined
def test_form_undefined_values():
    form = create_sample_form(assignment="field1 -> field2")
    form.field1 = LN_UNDEFINED
    form.field2 = PydanticUndefined

    assert not form.is_completed()
    assert not form.is_workable()

    results = form.to_dict(valid_only=True)
    assert "field1" not in results
    assert "field2" not in results


# Test inheritance
def test_form_inheritance():
    class CustomForm(Form):
        custom_field: str = Field(default="custom")

    form = CustomForm(assignment="field1 -> field2, custom_field")
    assert form.custom_field == "custom"
    assert isinstance(form, Form)
    assert isinstance(form, BaseForm)
    assert isinstance(form, Component)


# Test with various data types
def test_form_various_data_types():
    class ComplexForm(Form):
        string_field: str = Field(default="")
        int_field: int = Field(default=0)
        float_field: float = Field(default=0.0)
        bool_field: bool = Field(default=False)
        list_field: list = Field(default_factory=list)
        dict_field: dict = Field(default_factory=dict)

    form = ComplexForm(
        assignment="string_field, int_field -> float_field, bool_field, list_field, dict_field"
    )
    form.string_field = "test"
    form.int_field = 42
    form.float_field = 3.14
    form.bool_field = True
    form.list_field = [1, 2, 3]
    form.dict_field = {"key": "value"}

    assert form.is_completed()
    assert form.is_workable()


# Test Form with large number of fields
# @pytest.mark.slow
def test_form_large_number_of_fields():
    class LargeForm(Form):
        pass

    num_fields = 1000
    input_fields = [f"input_{i}" for i in range(num_fields // 2)]
    output_fields = [f"output_{i}" for i in range(num_fields // 2)]

    assignment = f"{','.join(input_fields)} -> {','.join(output_fields)}"
    form = LargeForm(assignment=assignment)

    for field in input_fields:
        setattr(form, field, f"value_{field}")

    assert form.is_workable()
    assert not form.is_completed()

    for field in output_fields:
        setattr(form, field, f"value_{field}")

    assert form.is_completed()


# Test Form performance
# @pytest.mark.slow
def test_form_performance():
    import time

    class PerformanceForm(Form):
        pass

    num_fields = 1000
    input_fields = [f"input_{i}" for i in range(num_fields // 2)]
    output_fields = [f"output_{i}" for i in range(num_fields // 2)]

    assignment = f"{','.join(input_fields)} -> {','.join(output_fields)}"

    start_time = time.time()
    form = PerformanceForm(assignment=assignment)
    for field in input_fields + output_fields:
        setattr(form, field, f"value_{field}")
    _ = form.to_dict()
    _ = form.is_completed()
    _ = form.is_workable()
    end_time = time.time()

    assert end_time - start_time < 2


# Test Form with nested structures
def test_form_nested_structures():
    class NestedForm(Form):
        nested_dict: dict = Field(default_factory=dict)
        nested_list: list = Field(default_factory=list)

    form = NestedForm(assignment="nested_dict -> nested_list")
    form.nested_dict = {"level1": {"level2": "value"}}
    form.nested_list = [1, [2, 3], {"key": "value"}]

    assert form.is_completed()
    assert form.is_workable()


# Test Form with strict mode
def test_form_strict_mode():
    form = create_sample_form(assignment="field1 -> field2", strict_form=True)

    with pytest.raises(LionOperationError):
        form.append_to_input("new_input")

    with pytest.raises(LionOperationError):
        form.append_to_request("new_request")


# Test Form with none_as_valid_value
def test_form_none_as_valid_value():
    form = create_sample_form(
        assignment="field1 -> field2", none_as_valid_value=True
    )
    form.field1 = None
    form.field2 = None
    assert form.is_completed()
    assert form.is_workable()


# Comprehensive test combining multiple aspects
def test_form_comprehensive():
    class ComprehensiveForm(Form):
        input_field: str | None = Field(default=LN_UNDEFINED)
        process_field: int | None = Field(default=LN_UNDEFINED)
        output_field: list | LionUndefinedType = Field(default=LN_UNDEFINED)

    form = ComprehensiveForm(
        assignment="input_field -> process_field, output_field",
        guidance="Comprehensive test guidance",
        task_description="Comprehensive test description",
        output_fields=["output_field"],
        none_as_valid_value=True,
    )

    # Test basic functionality
    assert form.input_fields == ["input_field"]
    assert form.request_fields == ["process_field", "output_field"]
    assert form.output_fields == ["output_field"]
    assert form.guidance == "Comprehensive test guidance"
    assert form.task_description == "Comprehensive test description"

    # Test workability and completion
    assert not form.is_workable()
    assert not form.is_completed()

    form.input_field = "test_input"
    assert form.is_workable()
    assert not form.is_completed()

    form.process_field = 42
    form.output_field = [1, 2, 3]
    assert form.is_workable()
    assert form.is_completed()

    # Test get_results with different parameters
    full_results = form.get_results()
    assert full_results == {"output_field": [1, 2, 3]}

    # Test with undefined values
    form.output_field = LN_UNDEFINED
    undefined_results = form.get_results(valid_only=True)
    assert "output_field" not in undefined_results

    # Test serialization and deserialization
    serialized = form.to_dict()
    deserialized = ComprehensiveForm.from_dict(serialized)
    assert deserialized.input_field == "test_input"
    assert deserialized.process_field == 42
    assert deserialized.output_field == LN_UNDEFINED

    # Test dynamic field addition
    form.append_to_input("dynamic_input", value="dynamic")
    assert "dynamic_input" in form.input_fields
    assert "dynamic_input" in form.assignment

    form.append_to_request("dynamic_request")
    assert "dynamic_request" in form.request_fields
    assert "dynamic_request" in form.assignment

    form.append_to_output("dynamic_output")
    assert "dynamic_output" in form.output_fields

    # Test fill methods
    new_form = ComprehensiveForm(
        assignment="input_field, dynamic_input -> process_field, output_field"
    )
    new_form.fill_input_fields(form)
    assert new_form.input_field == "test_input"
    assert new_form.dynamic_input == "dynamic"

    new_form.fill_request_fields(form)
    assert new_form.process_field == 42
    assert new_form.output_field == LN_UNDEFINED

    # Test remove_request_from_output
    new_form.remove_request_from_output()
    assert "process_field" not in new_form.output_fields
    assert "output_field" not in new_form.output_fields

    # Ensure all operations maintain the integrity of the form
    assert isinstance(form, Form)
    assert isinstance(form, BaseForm)
    assert isinstance(form, Component)


# Test Form with Note object
def test_form_with_note():
    note_data = Note(**{"assignment": "field1 -> field2", "field1": "value1"})
    form = Form.from_dict(note_data)
    assert form.assignment == "field1 -> field2"
    assert form.field1 == "value1"


# Test Form with empty assignment
def test_form_empty_assignment():
    with pytest.raises(ValueError):
        Form(assignment="")


# Test Form with very long assignment
def test_form_long_assignment():
    long_input = ",".join([f"input_{i}" for i in range(1000)])
    long_output = ",".join([f"output_{i}" for i in range(1000)])
    long_assignment = f"{long_input} -> {long_output}"

    form = Form(assignment=long_assignment)
    assert len(form.input_fields) == 1000
    assert len(form.request_fields) == 1000


# Test Form with circular dependency
def test_form_circular_dependency():
    form = Form(assignment="field1 -> field1")
    assert form.input_fields == ["field1"]
    assert form.request_fields == ["field1"]


# Test Form with special characters in field names
def test_form_special_characters():
    form = Form(assignment="field-1, field_2 -> field.3")
    assert form.input_fields == ["field-1", "field_2"]
    assert form.request_fields == ["field.3"]


# Test Form with unicode characters
def test_form_unicode_characters():
    form = Form(assignment="字段1 -> フィールド2")
    assert form.input_fields == ["字段1"]
    assert form.request_fields == ["フィールド2"]


# Test Form with very large field values
def test_form_large_field_values():
    class LargeValueForm(Form):
        large_field: str = Field(default="")

    form = LargeValueForm(assignment="large_field -> large_field")
    large_value = "a" * 10**6  # 1MB string
    form.large_field = large_value

    assert form.is_completed()
    assert form.is_workable()
    assert len(form.to_dict()["large_field"]) == 10**6


# Test Form with concurrent modifications
@pytest.mark.asyncio
async def test_form_concurrent_modifications():
    import asyncio

    class ConcurrentForm(Form):
        counter: int = Field(default=0)

    form = ConcurrentForm(assignment="counter -> counter")

    async def increment_counter():
        current = form.counter
        await asyncio.sleep(0.01)  # Simulate some processing time
        form.counter = current + 1

    tasks = [increment_counter() for _ in range(100)]
    await asyncio.gather(*tasks)

    assert form.counter > 0  # The exact value may vary due to race conditions


# Test Form with inheritance chain
def test_form_inheritance_chain():
    class BaseCustomForm(Form):
        base_field: str = Field(default="base")

    class MiddleCustomForm(BaseCustomForm):
        middle_field: str = Field(default="middle")

    class FinalCustomForm(MiddleCustomForm):
        final_field: str = Field(default="final")

    form = FinalCustomForm(
        assignment="base_field, middle_field -> final_field"
    )
    assert "base_field" in form.input_fields
    assert "middle_field" in form.input_fields
    assert "final_field" in form.request_fields


# Test Form with dynamic field type changes
def test_form_dynamic_field_type_changes():
    class DynamicTypeForm(Form):
        dynamic_field: Any = Field(default=None)

    form = DynamicTypeForm(assignment="dynamic_field -> dynamic_field")

    form.dynamic_field = "string"
    assert isinstance(form.dynamic_field, str)

    form.dynamic_field = 42
    assert isinstance(form.dynamic_field, int)

    form.dynamic_field = [1, 2, 3]
    assert isinstance(form.dynamic_field, list)


# Test Form with custom serialization/deserialization
def test_form_custom_serialization():
    class CustomSerializeForm(Form):
        date_field: str = Field(default="")

        def to_dict(self):
            data = super().to_dict()
            if self.date_field:
                data["date_field"] = f"Custom: {self.date_field}"
            return data

        @classmethod
        def from_dict(cls, data):
            if "date_field" in data and data["date_field"].startswith(
                "Custom: "
            ):
                data["date_field"] = data["date_field"][8:]
            return super().from_dict(data)

    form = CustomSerializeForm(assignment="date_field -> date_field")
    form.date_field = "2023-01-01"

    serialized = form.to_dict()
    assert serialized["date_field"] == "Custom: 2023-01-01"

    deserialized = CustomSerializeForm.from_dict(serialized)
    assert deserialized.date_field == "2023-01-01"


# Test Form with complex nested structures
def test_form_complex_nested_structures():
    class ComplexNestedForm(Form):
        nested_field: dict = Field(default_factory=dict)

    form = ComplexNestedForm(assignment="nested_field -> nested_field")
    form.nested_field = {
        "level1": {"level2": [{"key": "value"}, [1, 2, {"nested": "deep"}]]}
    }

    assert form.is_completed()
    serialized = form.to_dict()
    deserialized = ComplexNestedForm.from_dict(serialized)
    assert deserialized.nested_field == form.nested_field


# Final comprehensive test
def test_form_final_comprehensive():
    class FinalForm(Form):
        input1: str | None = Field(default=None)
        input2: int | None = Field(default=None)
        process: dict | None = Field(default=None)
        output: list | None = Field(default=None)

    form = FinalForm(
        assignment="input1, input2 -> process, output",
        guidance="Final comprehensive test",
        task_description="Testing all aspects of Form",
        output_fields=["output"],
    )

    # Test initialization and basic properties
    assert form.input_fields == ["input1", "input2"]
    assert form.request_fields == ["process", "output"]
    assert form.output_fields == ["output"]
    assert form.guidance == "Final comprehensive test"
    assert form.task_description == "Testing all aspects of Form"

    # Test setting values and checking completion
    form.input1 = "test"
    form.input2 = 42
    assert form.is_workable()
    assert not form.is_completed()

    form.process = {"key": "value"}
    form.output = [1, 2, 3]
    assert form.is_completed()

    # Test getting results
    results = form.get_results()
    assert results == {"output": [1, 2, 3]}

    # Test serialization and deserialization
    serialized = form.to_dict()
    deserialized = FinalForm.from_dict(serialized)
    assert deserialized.input1 == "test"
    assert deserialized.input2 == 42
    assert deserialized.process == {"key": "value"}
    assert deserialized.output == [1, 2, 3]

    # Test dynamic field operations
    form.append_to_input("dynamic_input", value="dynamic")
    form.append_to_request("dynamic_request")
    form.append_to_output("dynamic_output")

    assert "dynamic_input" in form.input_fields
    assert "dynamic_request" in form.request_fields
    assert "dynamic_output" in form.output_fields

    # Test error handling
    with pytest.raises(LionValueError):
        form.append_to_request("invalid", value="not allowed")

    form.dynamic_request = "dynamic_request"
    form.dynamic_output = "dynamic_output"
    # Ensure the form still maintains its integrity after all operations
    assert isinstance(form, Form)
    assert isinstance(form, BaseForm)
    assert isinstance(form, Component)
    assert form.is_workable()
    assert form.is_completed()
