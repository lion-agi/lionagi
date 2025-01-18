"""Tests for the form module."""

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
    assert form.guidance is None
    assert form.task is None
    assert form.flow_definition is None


def test_parse_assignment_into_flow():
    """Test assignment parsing into flow."""
    # Single step - no flow
    form = Form(assignment="input -> output")
    assert form.flow_definition is None
    assert form.output_fields == ["output"]

    # Multi-step - creates flow
    form = Form(assignment="a->b; b->c")
    assert form.flow_definition is not None
    assert len(form.flow_definition.steps) == 2
    assert set(form.output_fields) == {"b", "c"}  # All produced fields


def test_compute_output_fields():
    """Test output fields computation."""
    # Simple assignment
    form = Form(assignment="x,y -> z")
    assert form.output_fields == ["z"]

    # Multi-step flow
    form = Form(assignment="a->b,c; c->d")
    assert set(form.output_fields) == {"b", "c", "d"}  # All produced fields

    # Explicit output_fields override computed ones
    form = Form(assignment="x->y", output_fields=["z"])
    assert form.output_fields == ["z"]


def test_fill_fields():
    """Test fill_fields method."""
    form = Form(assignment="input -> output")
    form.fill_fields(input="value1", output="value2")
    assert getattr(form, "input") == "value1"
    assert getattr(form, "output") == "value2"


def test_to_instructions():
    """Test to_instructions method."""
    # Simple form
    form = Form(
        assignment="input -> output",
        guidance="test guidance",
        task="test task",
    )
    instructions = form.to_instructions()
    assert instructions["assignment"] == "input -> output"
    assert instructions["guidance"] == "test guidance"
    assert instructions["task"] == "test task"
    assert instructions["flow"] is None
    assert instructions["required_outputs"] == ["output"]

    # Form with flow
    form = Form(assignment="a->b; b->c")
    instructions = form.to_instructions()
    assert instructions["flow"] is not None
    assert len(instructions["flow"]["steps"]) == 2
    assert set(instructions["required_outputs"]) == {"b", "c"}


def test_form_with_none_values():
    """Test form behavior with None values."""
    form = SimpleTaskForm(
        assignment="input_value -> output_value", none_as_valid=True
    )

    # None should be valid
    form.input_value = None
    form.output_value = None
    assert form.is_completed()

    # Change to not accept None
    form.none_as_valid = False
    assert not form.is_completed()


def test_form_completeness():
    """Test form completion checks."""
    form = SimpleTaskForm(assignment="input_value -> output_value")

    # Initially incomplete
    assert not form.is_completed()

    # Fill required fields
    form.input_value = "test input"
    form.output_value = "test output"
    assert form.is_completed()

    # Optional fields don't affect completeness
    form.optional_value = None
    assert form.is_completed()
