from enum import Enum

import pytest
from pydantic import BaseModel, ValidationError

from lionagi.integrations.anthropic_.api_endpoints.data_models import (
    AnthropicEndpointPathParam,
    AnthropicEndpointQueryParam,
    AnthropicEndpointRequestBody,
    AnthropicEndpointResponseBody,
)


class SampleEnum(str, Enum):  # Make it a str enum for proper serialization
    VALUE1 = "value1"
    VALUE2 = "value2"


class SampleRequestModel(AnthropicEndpointRequestBody):
    field1: str
    field2: int
    enum_field: SampleEnum | None = None


class SampleResponseModel(AnthropicEndpointResponseBody):
    field1: str
    field2: int
    enum_field: SampleEnum | None = None


class SampleQueryParam(AnthropicEndpointQueryParam):
    param1: str
    param2: int | None = None


class SamplePathParam(AnthropicEndpointPathParam):
    param1: str
    param2: int | None = None


def test_query_param_validation():
    # Test valid query params
    params = SampleQueryParam(param1="test")
    assert params.param1 == "test"
    assert params.param2 is None

    # Test all fields
    params = SampleQueryParam(param1="test", param2=123)
    assert params.param1 == "test"
    assert params.param2 == 123

    # Test extra fields forbidden
    with pytest.raises(ValidationError):
        SampleQueryParam(param1="test", extra_param="invalid")

    # Test assignment validation
    params = SampleQueryParam(param1="test")
    with pytest.raises(ValidationError):
        params.param2 = "invalid_type"  # should be int or None


def test_path_param_validation():
    # Test valid path params
    params = SamplePathParam(param1="test")
    assert params.param1 == "test"
    assert params.param2 is None

    # Test all fields
    params = SamplePathParam(param1="test", param2=123)
    assert params.param1 == "test"
    assert params.param2 == 123

    # Test extra fields forbidden
    with pytest.raises(ValidationError):
        SamplePathParam(param1="test", extra_param="invalid")

    # Test assignment validation
    params = SamplePathParam(param1="test")
    with pytest.raises(ValidationError):
        params.param2 = "invalid_type"  # should be int or None


def test_model_inheritance():
    # Test that child models properly inherit configuration

    # Test request body inheritance
    class ChildRequestModel(SampleRequestModel):
        child_field: str

    request = ChildRequestModel(field1="test", field2=123, child_field="child")
    assert request.field1 == "test"
    assert request.child_field == "child"
    with pytest.raises(ValidationError):
        ChildRequestModel(
            field1="test", field2=123, child_field="child", extra="invalid"
        )

    # Test response body inheritance
    class ChildResponseModel(SampleResponseModel):
        child_field: str

    response = ChildResponseModel(
        field1="test", field2=123, child_field="child"
    )
    assert response.field1 == "test"
    assert response.child_field == "child"

    # Test query param inheritance
    class ChildQueryParam(SampleQueryParam):
        child_param: str

    params = ChildQueryParam(param1="test", child_param="child")
    assert params.param1 == "test"
    assert params.child_param == "child"
    with pytest.raises(ValidationError):
        ChildQueryParam(param1="test", child_param="child", extra="invalid")

    # Test path param inheritance
    class ChildPathParam(SamplePathParam):
        child_param: str

    params = ChildPathParam(param1="test", child_param="child")
    assert params.param1 == "test"
    assert params.child_param == "child"
    with pytest.raises(ValidationError):
        ChildPathParam(param1="test", child_param="child", extra="invalid")
