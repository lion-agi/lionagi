"""Tests for the instruct module."""

import pytest
from pydantic import JsonValue, ValidationError

from lionagi.protocols.operatives.instruct import (
    ACTIONS_FIELD,
    CONTEXT_FIELD,
    GUIDANCE_FIELD,
    INSTRUCTION_FIELD,
    REASON_FIELD,
    Instruct,
    OperationInstruct,
    validate_boolean_field,
    validate_instruction,
)


class TestValidators:
    def test_validate_instruction(self):
        """Test instruction validator with various inputs."""
        # Valid cases
        assert (
            validate_instruction(None, "test instruction")
            == "test instruction"
        )
        assert validate_instruction(None, {"key": "value"}) == {"key": "value"}
        assert validate_instruction(None, ["item1", "item2"]) == [
            "item1",
            "item2",
        ]

        # Invalid cases
        assert validate_instruction(None, None) is None
        assert validate_instruction(None, "") is None
        assert validate_instruction(None, "   ") is None

    def test_validate_boolean_field(self):
        """Test boolean field validator with various inputs."""
        # Valid cases
        assert validate_boolean_field(None, True) is True
        assert validate_boolean_field(None, False) is False
        assert validate_boolean_field(None, "true") is True
        assert validate_boolean_field(None, "false") is False
        assert validate_boolean_field(None, 1) is True
        assert validate_boolean_field(None, 0) is False

        # Invalid cases
        assert validate_boolean_field(None, None) is None
        assert validate_boolean_field(None, "invalid") is None
        assert validate_boolean_field(None, {}) is None


class TestInstructModel:
    def test_valid_instruction(self):
        """Test Instruct model with valid instruction."""
        model = Instruct(instruction="test instruction")
        assert model.instruction == "test instruction"
        assert model.guidance is None
        assert model.context is None

    def test_empty_instruction(self):
        """Test Instruct model with empty instruction."""
        model = Instruct(instruction=None)
        assert model.instruction is None

        model = Instruct(instruction="")
        assert model.instruction is None

        model = Instruct(instruction="   ")
        assert model.instruction is None

    def test_complex_instruction(self):
        """Test Instruct model with complex instruction types."""
        # Dictionary instruction
        dict_instruction = {
            "task": "analyze",
            "target": "data",
            "parameters": {"param1": "value1"},
        }
        model = Instruct(instruction=dict_instruction)
        assert model.instruction == dict_instruction

        # List instruction
        list_instruction = ["step1", "step2", "step3"]
        model = Instruct(instruction=list_instruction)
        assert model.instruction == list_instruction

    def test_guidance_field(self):
        """Test Instruct model with guidance field."""
        guidance = {
            "methods": ["method1", "method2"],
            "constraints": {"time": "1h", "memory": "1GB"},
        }
        model = Instruct(instruction="test", guidance=guidance)
        assert model.guidance == guidance

    def test_context_field(self):
        """Test Instruct model with context field."""
        context = {
            "environment": "production",
            "dependencies": ["dep1", "dep2"],
            "prior_results": {"accuracy": 0.95},
        }
        model = Instruct(instruction="test", context=context)
        assert model.context == context

    def test_full_model(self):
        """Test Instruct model with all fields."""
        data = {
            "instruction": "test instruction",
            "guidance": {"method": "test_method"},
            "context": {"env": "test_env"},
        }
        model = Instruct(**data)
        assert model.instruction == data["instruction"]
        assert model.guidance == data["guidance"]
        assert model.context == data["context"]


class TestOperationInstructModel:
    def test_default_values(self):
        """Test OperationInstruct model default values."""
        model = OperationInstruct()
        assert model.instruction is None
        assert model.reason is False
        assert model.actions is False

    def test_with_instruct(self):
        """Test OperationInstruct model with Instruct object."""
        instruct = Instruct(instruction="test instruction")
        model = OperationInstruct(**instruct.model_dump())
        assert model.instruction == instruct.instruction
        assert model.instruction == "test instruction"

    def test_boolean_fields(self):
        """Test OperationInstruct model boolean fields."""
        # Test with explicit boolean values
        model = OperationInstruct(reason=True, actions=True)
        assert model.reason is True
        assert model.actions is True

        # Test with string values
        model = OperationInstruct(reason="true", actions="false")
        assert model.reason is True
        assert model.actions is False

        # Test with numeric values
        model = OperationInstruct(reason=1, actions=0)
        assert model.reason is True
        assert model.actions is False

    def test_full_model(self):
        """Test OperationInstruct model with all fields."""
        instruct = Instruct(
            instruction="test instruction",
            guidance={"method": "test_method"},
            context={"env": "test_env"},
        )
        model = OperationInstruct(
            **instruct.model_dump(), reason=True, actions=True
        )
        assert model.instruction == instruct.instruction
        assert model.reason is True
        assert model.actions is True


class TestFieldModels:
    def test_instruction_field(self):
        """Test INSTRUCTION_FIELD configuration."""
        assert INSTRUCTION_FIELD.name == "instruction"
        assert INSTRUCTION_FIELD.annotation == (JsonValue | None)
        assert INSTRUCTION_FIELD.default is None
        assert INSTRUCTION_FIELD.validator == validate_instruction

    def test_guidance_field(self):
        """Test GUIDANCE_FIELD configuration."""
        assert GUIDANCE_FIELD.name == "guidance"
        assert GUIDANCE_FIELD.annotation == (JsonValue | None)
        assert GUIDANCE_FIELD.default is None

    def test_context_field(self):
        """Test CONTEXT_FIELD configuration."""
        assert CONTEXT_FIELD.name == "context"
        assert CONTEXT_FIELD.annotation == (JsonValue | None)
        assert CONTEXT_FIELD.default is None

    def test_reason_field(self):
        """Test REASON_FIELD configuration."""
        assert REASON_FIELD.name == "reason"
        assert REASON_FIELD.annotation == bool
        assert REASON_FIELD.default is False
        assert REASON_FIELD.validator == validate_boolean_field

    def test_actions_field(self):
        """Test ACTIONS_FIELD configuration."""
        assert ACTIONS_FIELD.name == "actions"
        assert ACTIONS_FIELD.annotation == bool
        assert ACTIONS_FIELD.default is False
        assert ACTIONS_FIELD.validator == validate_boolean_field
