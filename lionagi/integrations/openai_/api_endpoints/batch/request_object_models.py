from typing import Literal

from pydantic import BaseModel, Field, SerializeAsAny

from ..data_models import OpenAIEndpointRequestBody
from .types import Endpoint


class Response(BaseModel):
    status_code: int = Field(
        description="The HTTP status code of the response."
    )

    request_id: str = Field(
        description="An unique identifier for the OpenAI API request. "
        "Please include this request ID when contacting support."
    )

    body: dict = Field(description="The JSON body of the response")


class Error(BaseModel):
    code: str = Field(description="A machine-readable error code.")

    message: str = Field(description="A human-readable error message.")


class OpenAIBatchRequestInputObject(BaseModel):
    custom_id: str = Field(
        description="A developer-provided per-request id "
        "that will be used to match outputs to inputs. "
        "Must be unique for each request in a batch."
    )

    method: Literal["POST"] = Field(
        description="The HTTP method to be used for the "
        "request. Currently only POST is supported."
    )

    url: Endpoint = Field(
        description="The OpenAI API relative URL to be"
        " used for the request."
    )

    body: SerializeAsAny[OpenAIEndpointRequestBody] = Field(
        description="the parameters for the underlying endpoint."
    )


class OpenAIBatchRequestOutputObject(BaseModel):
    id: str = Field(description="The output object id.")

    custom_id: str = Field(
        description="A developer-provided per-request id"
        " that will be used to match outputs to inputs."
    )

    response: Response | None = Field(
        description="The endpoint response body."
    )

    error: Error | None = Field(
        description="For requests that failed with a non-HTTP error, "
        "this will contain more information on the cause of the failure."
    )
