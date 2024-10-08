import pytest
from lionfuncs import LN_UNDEFINED
from pydantic import Field
from pydantic_core import PydanticUndefined

from lion_core.form.base import BaseForm
from lion_core.generic.component import Component


# Helper functions and classes
def create_sample_base_form(**kwargs):
    class SampleBaseForm(BaseForm):
        field1: str = Field(default="")
        field2: int = Field(default=0)

    return SampleBaseForm(**kwargs)


# Test BaseForm initialization and basic properties
def test_base_form_init():
    form = BaseForm(assignment="input1, input2 -> output")
    assert form.assignment == "input1, input2 -> output"
    assert form.template_name == "default_form"
    assert form.output_fields == []
    assert not form.none_as_valid_value

    form_with_fields = create_sample_base_form(
        assignment="field1 -> field2", output_fields=["field1", "field2"]
    )
    assert form_with_fields.output_fields == ["field1", "field2"]


def test_base_form_output_fields_validator():
    form = BaseForm(output_fields="single_field")
    assert form.output_fields == ["single_field"]

    form = BaseForm(output_fields=["field1", "field2"])
    assert form.output_fields == ["field1", "field2"]

    with pytest.raises(ValueError):
        BaseForm(output_fields=123)


# Test BaseForm properties
def test_base_form_work_fields():
    form = create_sample_base_form(output_fields=["field1", "field2"])
    assert form.work_fields == ["field1", "field2"]


def test_base_form_work_dict():
    form = create_sample_base_form(output_fields=["field1", "field2"])
    form.field1 = "test_value"
    assert form.work_dict == {"field1": "test_value", "field2": 0}


def test_base_form_required_fields():
    form = create_sample_base_form(output_fields=["field1", "field2"])
    assert form.required_fields == ["field1", "field2"]


def test_base_form_required_dict():
    form = create_sample_base_form(output_fields=["field1", "field2"])
    form.field1 = "test_value"
    assert form.required_dict == {"field1": "test_value", "field2": 0}


def test_base_form_display_dict():
    form = create_sample_base_form(output_fields=["field1", "field2"])
    form.field1 = "test_value"
    assert form.display_dict == {"field1": "test_value", "field2": 0}


# Test BaseForm methods
def test_base_form_get_results():
    form = create_sample_base_form(output_fields=["field1", "field2"])
    form.field1 = "test_value"

    results = form.get_results()
    assert results == {"field1": "test_value", "field2": 0}

    results_valid_only = form.get_results(valid_only=True)
    assert results_valid_only == {"field1": "test_value", "field2": 0}

    form.field2 = None
    results_with_none = form.get_results(valid_only=True)
    assert results_with_none == {"field1": "test_value"}

    form.none_as_valid_value = True
    results_none_valid = form.get_results(valid_only=True)
    assert results_none_valid == {"field1": "test_value", "field2": None}


# Test error handling
def test_base_form_error_handling():
    with pytest.raises(ValueError):
        BaseForm(output_fields={"invalid": "type"})

    form = create_sample_base_form(output_fields=["field1", "non_existent"])
    with pytest.raises(ValueError):
        form.get_results()

    assert form.get_results(suppress=True) == {"field1": ""}


# Test with LN_UNDEFINED and PydanticUndefined
def test_base_form_undefined_values():
    form = create_sample_base_form(output_fields=["field1", "field2"])
    form.field1 = LN_UNDEFINED
    form.field2 = PydanticUndefined

    results = form.get_results()
    assert results["field1"] is LN_UNDEFINED
    assert results["field2"] is PydanticUndefined

    results_valid_only = form.get_results(valid_only=True)
    assert "field1" not in results_valid_only
    assert "field2" not in results_valid_only


# Test inheritance
def test_base_form_inheritance():
    class CustomBaseForm(BaseForm):
        custom_field: str = Field(default="custom")

    form = CustomBaseForm(output_fields=["custom_field"])
    assert form.custom_field == "custom"
    assert isinstance(form, BaseForm)
    assert isinstance(form, Component)


# Test with various data types
def test_base_form_various_data_types():
    class ComplexBaseForm(BaseForm):
        string_field: str = Field(default="")
        int_field: int = Field(default=0)
        float_field: float = Field(default=0.0)
        bool_field: bool = Field(default=False)
        list_field: list = Field(default_factory=list)
        dict_field: dict = Field(default_factory=dict)

    form = ComplexBaseForm(
        output_fields=[
            "string_field",
            "int_field",
            "float_field",
            "bool_field",
            "list_field",
            "dict_field",
        ]
    )
    form.string_field = "test"
    form.int_field = 42
    form.float_field = 3.14
    form.bool_field = True
    form.list_field = [1, 2, 3]
    form.dict_field = {"key": "value"}

    results = form.get_results()
    assert results["string_field"] == "test"
    assert results["int_field"] == 42
    assert results["float_field"] == 3.14
    assert results["bool_field"] is True
    assert results["list_field"] == [1, 2, 3]
    assert results["dict_field"] == {"key": "value"}


# Test BaseForm with large number of fields
# @pytest.mark.slow
def test_base_form_large_number_of_fields():
    class LargeBaseForm(BaseForm):
        pass

    num_fields = 1000
    output_fields = []
    for i in range(num_fields):
        field_name = f"field_{i}"
        setattr(LargeBaseForm, field_name, Field(default=""))
        output_fields.append(field_name)

    form = LargeBaseForm(output_fields=output_fields)

    for i in range(num_fields):
        form.add_field(f"field_{i}")
        setattr(form, f"field_{i}", f"value_{i}")

    results = form.get_results()
    assert len(results) == num_fields
    assert all(
        results[f"field_{i}"] == f"value_{i}" for i in range(num_fields)
    )


# Test BaseForm performance
# @pytest.mark.slow
def test_base_form_performance():
    import time

    class PerformanceBaseForm(BaseForm):
        pass

    num_fields = 1000
    output_fields = []
    for i in range(num_fields):
        field_name = f"field_{i}"
        setattr(PerformanceBaseForm, field_name, Field(default=""))
        output_fields.append(field_name)

    start_time = time.time()
    form = PerformanceBaseForm(output_fields=output_fields)
    for i in range(num_fields):
        form.add_field(f"field_{i}")
        setattr(form, f"field_{i}", f"value_{i}")
    _ = form.get_results()
    end_time = time.time()

    assert end_time - start_time < 1


# Test BaseForm with nested structures
def test_base_form_nested_structures():
    class NestedBaseForm(BaseForm):
        nested_dict: dict = Field(default_factory=dict)
        nested_list: list = Field(default_factory=list)

    form = NestedBaseForm(output_fields=["nested_dict", "nested_list"])
    form.nested_dict = {"level1": {"level2": "value"}}
    form.nested_list = [1, [2, 3], {"key": "value"}]

    results = form.get_results()
    assert results["nested_dict"] == {"level1": {"level2": "value"}}
    assert results["nested_list"] == [1, [2, 3], {"key": "value"}]


# Test BaseForm serialization
def test_base_form_serialization():
    form = create_sample_base_form(
        assignment="field1 -> field2", output_fields=["field1", "field2"]
    )
    form.field1 = "test_value"
    form.field2 = 42

    serialized = form.to_dict()
    assert isinstance(serialized, dict)
    assert "field1" in serialized
    assert "field2" in serialized
    assert serialized["field1"] == "test_value"
    assert serialized["field2"] == 42

    deserialized = BaseForm.from_dict(serialized)
    assert deserialized.field1 == "test_value"
    assert deserialized.field2 == 42


# Test BaseForm with dynamic field addition
def test_base_form_dynamic_fields():
    form = BaseForm()
    form.add_field("dynamic_field", field_obj=Field(default="dynamic"))
    form.output_fields.append("dynamic_field")

    assert "dynamic_field" in form.all_fields
    assert form.get_results()["dynamic_field"] == "dynamic"


# Comprehensive test combining multiple aspects
def test_base_form_comprehensive():
    class ComprehensiveBaseForm(BaseForm):
        string_field: str = Field(default="")
        int_field: int = Field(default=0)
        list_field: list = Field(default_factory=list)

    form = ComprehensiveBaseForm(
        assignment="string_field, int_field -> list_field",
        output_fields=["string_field", "int_field", "list_field"],
    )

    form.string_field = "test"
    form.int_field = 42
    form.list_field = [1, 2, 3]

    # Test basic functionality
    assert form.work_fields == ["string_field", "int_field", "list_field"]
    assert form.required_fields == ["string_field", "int_field", "list_field"]

    # Test get_results with different parameters
    full_results = form.get_results()
    assert full_results == {
        "string_field": "test",
        "int_field": 42,
        "list_field": [1, 2, 3],
    }

    valid_results = form.get_results(valid_only=True)
    assert valid_results == full_results

    # Test with undefined values
    form.string_field = LN_UNDEFINED
    undefined_results = form.get_results(valid_only=True)
    assert "string_field" not in undefined_results

    # Test serialization and deserialization
    form.string_field = ""
    serialized = form.to_dict()
    deserialized = ComprehensiveBaseForm.from_dict(serialized)
    assert deserialized.int_field == 42
    assert deserialized.list_field == [1, 2, 3]

    # Test dynamic field addition
    form.add_field("dynamic_field", Field(default="dynamic"))
    form.output_fields.append("dynamic_field")
    assert "dynamic_field" in form.get_results()

    # Ensure all operations maintain the integrity of the form
    assert isinstance(form, BaseForm)
    assert isinstance(form, Component)
    assert len(form.output_fields) == 4
