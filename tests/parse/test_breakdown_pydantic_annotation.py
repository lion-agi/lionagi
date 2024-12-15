from typing import Any, List

import pytest
from pydantic import BaseModel

from lionagi.libs.parse.breakdown_pydantic_annotation import (
    _is_pydantic_model,
    breakdown_pydantic_annotation,
)


class SimpleModel(BaseModel):
    field1: int
    field2: str


class NestedModel(BaseModel):
    simple: SimpleModel
    name: str


class ListModel(BaseModel):
    items: list[SimpleModel]
    count: int


class DeepNestedModel(BaseModel):
    nested: NestedModel
    list_field: list[ListModel]
    value: float


def test_simple_model():
    result = breakdown_pydantic_annotation(SimpleModel)
    assert result == {"field1": int, "field2": str}


def test_nested_model():
    result = breakdown_pydantic_annotation(NestedModel)
    assert result == {
        "simple": {"field1": int, "field2": str},
        "name": str,
    }


def test_list_model():
    result = breakdown_pydantic_annotation(ListModel)
    assert result == {
        "items": [{"field1": int, "field2": str}],
        "count": int,
    }


def test_deep_nested_model():
    result = breakdown_pydantic_annotation(DeepNestedModel)
    assert result == {
        "nested": {
            "simple": {"field1": int, "field2": str},
            "name": str,
        },
        "list_field": [
            {
                "items": [{"field1": int, "field2": str}],
                "count": int,
            }
        ],
        "value": float,
    }


def test_max_depth():
    with pytest.raises(
        RecursionError, match="Maximum recursion depth reached"
    ):
        breakdown_pydantic_annotation(DeepNestedModel, max_depth=1)


def test_invalid_input():
    class NotPydanticModel:
        field: str

    with pytest.raises(TypeError, match="Input must be a Pydantic model"):
        breakdown_pydantic_annotation(NotPydanticModel)


def test_list_with_non_pydantic():
    class ModelWithSimpleList(BaseModel):
        items: list[int]
        name: str

    result = breakdown_pydantic_annotation(ModelWithSimpleList)
    assert result == {
        "items": [int],
        "name": str,
    }


def test_list_with_any():
    class ModelWithAnyList(BaseModel):
        items: list
        name: str

    result = breakdown_pydantic_annotation(ModelWithAnyList)
    assert result == {
        "items": [Any],
        "name": str,
    }


def test_is_pydantic_model():
    assert _is_pydantic_model(SimpleModel) is True
    assert _is_pydantic_model(NestedModel) is True
    assert _is_pydantic_model(int) is False
    assert _is_pydantic_model("not a class") is False

    class NotPydanticModel:
        pass

    assert _is_pydantic_model(NotPydanticModel) is False
