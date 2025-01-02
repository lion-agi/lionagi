"""Tests for ModelParams class."""

import pytest
from pydantic import BaseModel, ConfigDict, Field

from lionagi.operatives.models.field_model import FieldModel
from lionagi.operatives.models.model_params import ModelParams


class TestModelParams:
    """Test suite for ModelParams class."""

    def test_basic_model_creation(self):
        """Test basic model creation with minimal parameters."""
        field1 = Field(default="test")
        field2 = Field(default=123)
        field1.annotation = str
        field2.annotation = int

        params = ModelParams(
            name="TestModel",
            parameter_fields={"field1": field1, "field2": field2},
            inherit_base=True,
        )

        model_class = params.create_new_model()
        assert model_class.__name__ == "TestModel"

        instance = model_class()
        assert instance.field1 == "test"
        assert instance.field2 == 123

    def test_model_with_base_type(self):
        """Test model creation with custom base type."""

        class CustomBase(BaseModel):
            base_field: str = "base"

        a = Field(default="test")
        a.annotation = str
        params = ModelParams(
            name="TestModel",
            base_type=CustomBase,
            parameter_fields={"field1": a},
        )

        model_class = params.create_new_model()
        instance = model_class()

        assert instance.base_field == "base"
        assert instance.field1 == "test"

    def test_model_with_field_models(self):
        """Test model creation with FieldModel instances."""
        field_model = FieldModel(
            name="test_field",
            annotation=str,
            default="test",
            description="A test field",
        )

        params = ModelParams(name="TestModel", field_models=[field_model])

        model_class = params.create_new_model()
        instance = model_class()

        assert instance.test_field == "test"
        assert (
            model_class.model_fields["test_field"].description
            == "A test field"
        )

    def test_model_with_validators(self):
        """Test model creation with field validators."""

        def validate_positive(value: int) -> int:
            if value <= 0:
                raise ValueError("Value must be positive")
            return value

        field_model = FieldModel(
            name="validated_field",
            annotation=int,
            default=1,
            validator=validate_positive,
        )

        params = ModelParams(name="TestModel", field_models=[field_model])

        model_class = params.create_new_model()

        # Valid value
        instance = model_class(validated_field=10)
        assert instance.validated_field == 10

        # Invalid value
        with pytest.raises(ValueError):
            model_class(validated_field=-1)

    def test_exclude_fields(self):
        """Test field exclusion functionality."""

        class BaseWithFields(BaseModel):
            keep_field: str = "keep"
            exclude_field: str = "exclude"

        params = ModelParams(
            name="TestModel",
            base_type=BaseWithFields,
            exclude_fields=["exclude_field"],
            inherit_base=False,
        )

        model_class = params.create_new_model()
        instance = model_class()

        assert hasattr(instance, "keep_field")
        assert not hasattr(instance, "exclude_field")

    def test_field_descriptions(self):
        """Test field description handling."""
        field_model = FieldModel(
            name="test_field", annotation=str, default="test"
        )

        params = ModelParams(
            name="TestModel",
            field_models=[field_model],
            field_descriptions={"test_field": "Updated description"},
        )

        model_class = params.create_new_model()
        assert (
            model_class.model_fields["test_field"].description
            == "Updated description"
        )

    def test_config_dict(self):
        """Test config dictionary handling."""
        a = Field(default="test")
        a.annotation = str
        params = ModelParams(
            name="TestModel",
            parameter_fields={"field1": a},
            config_dict=ConfigDict(frozen=True),
            inherit_base=False,
        )

        model_class = params.create_new_model()
        instance = model_class()

        # Should not be able to modify frozen model
        with pytest.raises(Exception):
            instance.field1 = "modified"

    def test_inherit_base_flag(self):
        """Test inherit_base flag behavior."""

        class CustomBase(BaseModel):
            base_field: str = "base"

        # With inheritance
        params = ModelParams(
            name="TestModel", base_type=CustomBase, inherit_base=True
        )

        model_class = params.create_new_model()
        assert issubclass(model_class, CustomBase)

        # Without inheritance
        params = ModelParams(
            name="TestModel", base_type=CustomBase, inherit_base=False
        )

        model_class = params.create_new_model()
        assert not issubclass(model_class, CustomBase)
        assert issubclass(model_class, BaseModel)

    def test_model_documentation(self):
        """Test model documentation handling."""
        doc = "This is a test model"
        a = Field(default="test")
        a.annotation = str
        params = ModelParams(
            name="TestModel",
            parameter_fields={"field1": a},
            doc=doc,
        )

        model_class = params.create_new_model()
        assert model_class.__doc__ == doc

    def test_frozen_model(self):
        """Test frozen model creation."""
        a = Field(annotation=str, default="test")
        a.annotation = str
        params = ModelParams(
            name="TestModel",
            parameter_fields={"field1": a},
            frozen=True,
        )

        model_class = params.create_new_model()
        instance = model_class()

        with pytest.raises(Exception):
            instance.field1 = "modified"

    def test_complex_model_creation(self):
        """Test creation of complex model with multiple features."""

        def validate_length(value: str) -> str:
            if len(value) < 3:
                raise ValueError("String too short")
            return value

        field_models = [
            FieldModel(
                name="validated_field",
                annotation=str,
                default="test",
                validator=validate_length,
            ),
            FieldModel(
                name="optional_field", annotation=str | None, default=None
            ),
        ]
        a = Field(default="regular")
        a.annotation = str
        params = ModelParams(
            name="ComplexModel",
            field_models=field_models,
            parameter_fields={"regular_field": a},
            doc="A complex model with multiple features",
            config_dict=ConfigDict(extra="forbid"),
            inherit_base=False,
        )

        model_class = params.create_new_model()

        # Test instance creation
        instance = model_class()
        assert instance.validated_field == "test"
        assert instance.optional_field is None
        assert instance.regular_field == "regular"

        # Test validation
        with pytest.raises(ValueError):
            instance = model_class(validated_field="ab")

        # Test extra fields forbidden
        with pytest.raises(ValueError):
            instance = model_class(extra_field="extra")

    def test_error_handling(self):
        """Test error handling in model creation."""
        # Invalid base type
        with pytest.raises(ValueError):
            ModelParams(name="TestModel", base_type=str)

        # Invalid field models
        with pytest.raises(ValueError):
            ModelParams(name="TestModel", field_models=["not a field model"])

        # Invalid parameter fields
        with pytest.raises(ValueError):
            ModelParams(
                name="TestModel",
                parameter_fields={"field": "not a field info"},
            )
