"""Tests for the flow module."""

import pytest

from lionagi.operatives.forms.flow import FlowDefinition, FlowStep


def test_flow_step_initialization():
    """Test basic initialization of FlowStep."""
    step = FlowStep(
        name="step_1",
        inputs=["a", "b"],
        outputs=["c"],
    )
    assert step.name == "step_1"
    assert step.inputs == ["a", "b"]
    assert step.outputs == ["c"]
    assert step.description is None


def test_flow_step_with_description():
    """Test FlowStep with description."""
    step = FlowStep(
        name="step_1",
        inputs=["x"],
        outputs=["y"],
        description="Transform x into y",
    )
    assert step.description == "Transform x into y"


def test_flow_step_validation():
    """Test FlowStep validation."""
    # Missing required fields should raise
    with pytest.raises(ValueError):
        FlowStep(name="step_1")  # missing inputs and outputs

    with pytest.raises(ValueError):
        FlowStep(
            name="step_1",
            inputs=["a"],  # missing outputs
        )


def test_flow_definition_initialization():
    """Test basic initialization of FlowDefinition."""
    flow = FlowDefinition()
    assert flow.steps == []


def test_parse_flow_string_single_step():
    """Test parsing a single-step flow string."""
    flow = FlowDefinition()
    flow.parse_flow_string("a,b->c")

    assert len(flow.steps) == 1
    step = flow.steps[0]
    assert step.name == "step_1"
    assert step.inputs == ["a", "b"]
    assert step.outputs == ["c"]


def test_parse_flow_string_multi_step():
    """Test parsing a multi-step flow string."""
    flow = FlowDefinition()
    flow.parse_flow_string("a,b->c; c->d,e")

    assert len(flow.steps) == 2

    step1 = flow.steps[0]
    assert step1.name == "step_1"
    assert step1.inputs == ["a", "b"]
    assert step1.outputs == ["c"]

    step2 = flow.steps[1]
    assert step2.name == "step_2"
    assert step2.inputs == ["c"]
    assert step2.outputs == ["d", "e"]


def test_parse_flow_string_with_spaces():
    """Test parsing flow string with various spacing."""
    flow = FlowDefinition()
    flow.parse_flow_string("  a , b  ->  c  ;  c  ->  d  ")

    assert len(flow.steps) == 2
    assert flow.steps[0].inputs == ["a", "b"]
    assert flow.steps[0].outputs == ["c"]
    assert flow.steps[1].inputs == ["c"]
    assert flow.steps[1].outputs == ["d"]


def test_parse_flow_string_empty():
    """Test parsing empty or None flow string."""
    flow = FlowDefinition()

    # Empty string should not create steps
    flow.parse_flow_string("")
    assert len(flow.steps) == 0

    # None should not create steps
    flow.parse_flow_string(None)
    assert len(flow.steps) == 0


def test_parse_flow_string_invalid():
    """Test parsing invalid flow strings."""
    flow = FlowDefinition()

    # Missing arrow
    with pytest.raises(ValueError, match="Invalid DSL segment"):
        flow.parse_flow_string("a,b,c")

    # Empty segments
    flow.parse_flow_string("a->b;;c->d")
    assert len(flow.steps) == 2  # Empty segments should be ignored


def test_get_required_fields():
    """Test getting required input fields."""
    flow = FlowDefinition()
    flow.parse_flow_string("x->y; y,z->w")

    required = flow.get_required_fields()
    assert required == {"x", "z"}  # x is needed for step1, z for step2
    # y is not required as it's produced by step1


def test_get_produced_fields():
    """Test getting produced output fields."""
    flow = FlowDefinition()
    flow.parse_flow_string("a->b,c; c->d")

    produced = flow.get_produced_fields()
    assert produced == {"b", "c", "d"}  # All outputs from all steps


def test_complex_flow():
    """Test a more complex flow with multiple dependencies."""
    flow = FlowDefinition()
    flow.parse_flow_string("a,b->c; c,d->e,f; f->g")

    required = flow.get_required_fields()
    assert required == {"a", "b", "d"}  # Initial inputs needed

    produced = flow.get_produced_fields()
    assert produced == {"c", "e", "f", "g"}  # All outputs

    # Verify step structure
    assert len(flow.steps) == 3
    assert flow.steps[0].inputs == ["a", "b"]
    assert flow.steps[1].inputs == ["c", "d"]
    assert flow.steps[2].inputs == ["f"]
