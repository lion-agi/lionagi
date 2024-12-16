"""Tests for OperableModel class."""

import pytest
from pydantic import Field
from pydantic.fields import FieldInfo

from lionagi.core.models import OperableModel, SchemaModel
from lionagi.libs.constants import UNDEFINED


class TestOperableModel:
    """Test suite for OperableModel class."""

    def test_basic_model_creation(self):
        """Test basic model creation with default fields."""

        class TestModel(OperableModel):
            field1: str = "test"
            field2: int = 123

        model = TestModel()
        assert model.field1 == "test"
        assert model.field2 == 123
        assert isinstance(model.extra_fields, dict)
        assert len(model.extra_fields) == 0

    def test_extra_fields_serialization(self):
        """Test serialization of extra fields."""

        class TestModel(OperableModel):
            base_field: str = "base"

        model = TestModel()
        model.extra_fields["extra_field"] = Field()
        object.__setattr__(model, "extra_field", "extra")

        result = model.to_dict()
        assert result["base_field"] == "base"
        assert result["extra_field"] == "extra"

    def test_nested_model_serialization(self):
        """Test serialization with nested models."""

        class NestedModel(SchemaModel):
            nested_field: str = "nested"

        class TestModel(OperableModel):
            base_field: str = "base"

        model = TestModel()
        nested = NestedModel()
        model.extra_fields["nested"] = Field()
        object.__setattr__(model, "nested", nested)

        result = model.to_dict()
        assert result["base_field"] == "base"
        assert isinstance(result["nested"], dict)
        assert result["nested"]["nested_field"] == "nested"

    def test_add_field_basic(self):
        """Test basic field addition."""
        model = OperableModel()
        model.extra_fields["new_field"] = Field()
        object.__setattr__(model, "new_field", "test")

        assert "new_field" in model.extra_fields
        assert model.new_field == "test"

    def test_add_field_with_annotation(self):
        """Test field addition with type annotation."""
        model = OperableModel()
        model.add_field("int_field", value=42, annotation=int)

        assert model.extra_fields["int_field"].annotation == int
        assert model.int_field == 42

    def test_add_field_with_field_info(self):
        """Test field addition with FieldInfo object."""
        model = OperableModel()
        field_obj = Field(default="test", description="Test field")
        model.extra_fields["field_info_test"] = field_obj
        object.__setattr__(model, "field_info_test", "test")

        assert model.field_info_test == "test"
        assert (
            model.extra_fields["field_info_test"].description == "Test field"
        )

    def test_add_duplicate_field(self):
        """Test adding duplicate field raises error."""
        model = OperableModel()
        model.extra_fields["test_field"] = Field()
        object.__setattr__(model, "test_field", "test")

        with pytest.raises(ValueError):
            model.add_field("test_field", value="duplicate")

    def test_update_field(self):
        """Test field update functionality."""
        model = OperableModel()
        model.extra_fields["test_field"] = Field()
        object.__setattr__(model, "test_field", "initial")

        model.update_field("test_field", value="updated")
        assert model.test_field == "updated"

    def test_update_field_attributes(self):
        """Test updating field attributes."""
        model = OperableModel()
        model.extra_fields["test_field"] = Field()
        object.__setattr__(model, "test_field", "test")

        model.field_setattr("test_field", "description", "Updated description")
        assert (
            model.extra_fields["test_field"].description
            == "Updated description"
        )

    def test_field_setattr(self):
        """Test setting field attributes."""
        model = OperableModel()
        model.extra_fields["test_field"] = Field()
        object.__setattr__(model, "test_field", "test")

        model.field_setattr("test_field", "description", "New description")
        assert (
            model.extra_fields["test_field"].description == "New description"
        )

    def test_field_getattr(self):
        """Test getting field attributes."""
        model = OperableModel()
        field_info = Field(description="Test description")
        model.extra_fields["test_field"] = field_info
        object.__setattr__(model, "test_field", "test")

        assert (
            model.field_getattr("test_field", "description")
            == "Test description"
        )

        # Test with default value
        assert (
            model.field_getattr("test_field", "nonexistent", "default")
            == "default"
        )

    def test_field_hasattr(self):
        """Test checking field attributes."""
        model = OperableModel()
        field_info = Field(description="Test description")
        model.extra_fields["test_field"] = field_info
        object.__setattr__(model, "test_field", "test")

        assert model.field_hasattr("test_field", "description")
        assert not model.field_hasattr("test_field", "nonexistent")

    def test_all_fields_property(self):
        """Test all_fields property."""

        class TestModel(OperableModel):
            base_field: str = "base"

        model = TestModel()
        model.extra_fields["extra_field"] = Field()
        object.__setattr__(model, "extra_field", "extra")

        all_fields = model.all_fields
        assert "base_field" in all_fields
        assert "extra_field" in all_fields
        assert "extra_fields" not in all_fields  # Should be excluded

    def test_complex_field_operations(self):
        """Test complex field operations."""
        model = OperableModel()

        # Add field with validator
        def validate_positive(value: int) -> int:
            if value <= 0:
                raise ValueError("Value must be positive")
            return value

        field_info = Field(annotation=int)
        model.extra_fields["validated_field"] = field_info
        object.__setattr__(model, "validated_field", 10)

        assert model.validated_field == 10

    def test_field_default_factory(self):
        """Test field with default_factory."""
        model = OperableModel()
        field_info = Field(default_factory=list)
        model.extra_fields["list_field"] = field_info
        object.__setattr__(model, "list_field", [])

        assert isinstance(model.list_field, list)
        assert len(model.list_field) == 0

    def test_invalid_field_operations(self):
        """Test invalid field operations."""
        model = OperableModel()

        # Test accessing non-existent field
        with pytest.raises(KeyError):
            model.field_getattr("nonexistent", "attr")

        # Test setting attributes on non-existent field
        with pytest.raises(KeyError):
            model.field_setattr("nonexistent", "attr", "value")

        # Test providing both default and default_factory
        with pytest.raises(ValueError):
            model.add_field(
                "invalid_field", default="value", default_factory=list
            )

    def test_nested_field_updates(self):
        """Test updating nested model fields."""

        class NestedModel(SchemaModel):
            nested_field: str = "nested"

        model = OperableModel()
        nested = NestedModel()
        model.extra_fields["nested"] = Field()
        object.__setattr__(model, "nested", nested)

        # Update nested model
        new_nested = NestedModel(nested_field="updated")
        object.__setattr__(model, "nested", new_nested)

        assert model.nested.nested_field == "updated"
        result = model.to_dict()
        assert result["nested"]["nested_field"] == "updated"
