"""Tests for BaseAutoModel class."""

import pytest
from pydantic import BaseModel, ConfigDict, Field

from lionagi.core.models import BaseAutoModel
from lionagi.libs.constants import UNDEFINED


class TestBaseAutoModel:
    """Test suite for BaseAutoModel class."""

    def test_to_dict_basic(self):
        """Test basic to_dict functionality."""

        class TestModel(BaseAutoModel):
            model_config = ConfigDict(validate_default=True)
            field1: str = "test"
            field2: int = 123
            field3: str | None = None

        model = TestModel()
        result = model.model_dump()

        assert isinstance(result, dict)
        assert result["field1"] == "test"
        assert result["field2"] == 123
        assert result["field3"] is None

    def test_to_dict_with_undefined(self):
        """Test to_dict handles UNDEFINED values correctly."""

        class TestModel(BaseAutoModel):
            model_config = ConfigDict(validate_default=True)
            field1: str = "test"
            field2: str | None = None

        model = TestModel()
        result = model.model_dump()

        assert "field1" in result
        assert result["field2"] is None

    def test_from_dict_basic(self):
        """Test basic from_dict functionality."""

        class TestModel(BaseAutoModel):
            field1: str
            field2: int
            field3: str | None = None

        test_data = {"field1": "test", "field2": 123, "field3": "value"}

        model = TestModel.from_dict(test_data)
        assert model.field1 == "test"
        assert model.field2 == 123
        assert model.field3 == "value"

    def test_from_dict_with_extra_fields(self):
        """Test from_dict with extra fields in input data."""

        class TestModel(BaseAutoModel):
            field1: str

        test_data = {"field1": "test", "extra_field": "extra"}

        model = TestModel.from_dict(test_data)
        assert model.field1 == "test"
        with pytest.raises(AttributeError):
            _ = model.extra_field

    def test_from_dict_with_missing_required(self):
        """Test from_dict with missing required fields."""

        class TestModel(BaseAutoModel):
            field1: str
            field2: int

        test_data = {"field1": "test"}

        with pytest.raises(ValueError):
            TestModel.from_dict(test_data)

    def test_hash_equality(self):
        """Test hash equality for identical models."""

        class TestModel(BaseAutoModel):
            model_config = ConfigDict(validate_default=True)
            field1: str = "test"
            field2: int = 123

        model1 = TestModel()
        model2 = TestModel()
        model3 = TestModel(field1="different")

        # Same content should produce same hash
        assert hash(model1) == hash(model2)
        # Different content should produce different hash
        assert hash(model1) != hash(model3)

    def test_nested_model(self):
        """Test handling of nested models."""

        class NestedModel(BaseAutoModel):
            model_config = ConfigDict(validate_default=True)
            nested_field: str = "nested"

        class TestModel(BaseAutoModel):
            model_config = ConfigDict(validate_default=True)
            field1: str = "test"
            nested: NestedModel = Field(default_factory=NestedModel)

        model = TestModel()
        result = model.model_dump()

        assert isinstance(result["nested"], dict)
        assert result["nested"]["nested_field"] == "nested"

    def test_complex_types(self):
        """Test handling of complex field types."""

        class TestModel(BaseAutoModel):
            model_config = ConfigDict(validate_default=True)
            list_field: list[int] = [1, 2, 3]
            dict_field: dict[str, str] = {"key": "value"}
            optional_field: str | None = None

        model = TestModel()
        result = model.model_dump()

        assert isinstance(result["list_field"], list)
        assert isinstance(result["dict_field"], dict)
        assert result["optional_field"] is None

    def test_model_validation(self):
        """Test model validation rules."""

        class TestModel(BaseAutoModel):
            age: int = Field(gt=0, lt=150)
            name: str = Field(min_length=2)

        # Valid data
        model = TestModel(age=25, name="John")
        assert model.age == 25
        assert model.name == "John"

        # Invalid age
        with pytest.raises(ValueError):
            TestModel(age=-1, name="John")

        # Invalid name
        with pytest.raises(ValueError):
            TestModel(age=25, name="J")

    def test_exclude_field(self):
        """Test field exclusion from serialization."""

        class TestModel(BaseAutoModel):
            model_config = ConfigDict(validate_default=True)
            public_field: str = "public"
            private_field: str = Field("private", exclude=True)

        model = TestModel()
        result = model.model_dump()

        assert "public_field" in result
        assert "private_field" not in result
