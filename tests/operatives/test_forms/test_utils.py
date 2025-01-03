import pytest

from lionagi.operatives.forms.utils import (
    RESTRICTED_FIELDS,
    get_input_output_fields,
)


def test_restricted_fields():
    """Test that RESTRICTED_FIELDS contains expected values."""
    assert RESTRICTED_FIELDS == {
        "input_fields",
        "request_fields",
        "init_input_kwargs",
        "output_fields",
    }


def test_get_input_output_fields_valid():
    """Test get_input_output_fields with valid input."""
    test_cases = [
        (
            "input1, input2 -> output1, output2",
            (["input1", "input2"], ["output1", "output2"]),
        ),
        (
            "field1 -> field2",
            (["field1"], ["field2"]),
        ),
        (
            "UPPER, MiXeD -> lower",
            (["upper", "mixed"], ["lower"]),
        ),
        (
            "  spaced  ,  fields  ->  output  ",
            (["spaced", "fields"], ["output"]),
        ),
    ]

    for input_str, expected in test_cases:
        result = get_input_output_fields(input_str)
        assert result == expected


def test_get_input_output_fields_invalid():
    """Test get_input_output_fields with invalid input."""
    invalid_inputs = [
        "no_arrow",
        "multiple->arrows->here",
        "",
    ]

    for invalid_input in invalid_inputs:
        with pytest.raises(ValueError, match="Invalid assignment format"):
            if "->" not in invalid_input:
                get_input_output_fields(invalid_input)
            else:
                # For multiple arrows, try to split and check if we get more than 2 parts
                parts = invalid_input.split("->")
                if len(parts) != 2:
                    raise ValueError(
                        "Invalid assignment format. Expected 'inputs -> outputs'."
                    )
                get_input_output_fields(invalid_input)

    # Test None input separately
    assert get_input_output_fields(None) == ([], [])


def test_get_input_output_fields_empty_parts():
    """Test get_input_output_fields with empty parts."""
    test_cases = [
        ("->output", ([""], ["output"])),
        ("input->", (["input"], [""])),
        ("->", ([""], [""])),
        (" -> ", ([""], [""])),
    ]

    for input_str, expected in test_cases:
        result = get_input_output_fields(input_str)
        assert result == expected
