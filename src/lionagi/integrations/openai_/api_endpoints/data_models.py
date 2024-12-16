from pydantic import BaseModel, ConfigDict


class OpenAIEndpointRequestBody(BaseModel):
    model_config = ConfigDict(
        extra="forbid", use_enum_values=True, validate_assignment=True
    )


class OpenAIEndpointResponseBody(BaseModel):
    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)


class OpenAIEndpointQueryParam(BaseModel):
    model_config = ConfigDict(
        extra="forbid", use_enum_values=True, validate_assignment=True
    )


class OpenAIEndpointPathParam(BaseModel):
    model_config = ConfigDict(
        extra="forbid", use_enum_values=True, validate_assignment=True
    )
