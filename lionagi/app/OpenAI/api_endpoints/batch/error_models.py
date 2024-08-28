from typing import Optional, List
from pydantic import Field
from .base_models import OpenAIBaseModel
from .types import ObjectTypeLiteral


class ErrorItem(OpenAIBaseModel):
    code: str = Field(
        ..., description="The error code.", example="invalid_request_error"
    )
    message: str = Field(
        ...,
        description="A human-readable error message.",
        example="The provided API key is invalid",
    )
    param: Optional[str] = Field(
        None, description="The parameter that caused the error, if applicable."
    )
    line: Optional[int] = Field(
        None, description="The line number where the error occurred, if applicable."
    )


class ErrorList(OpenAIBaseModel):
    object: ObjectTypeLiteral = Field(
        "list", description="The object type, which is always 'list'."
    )
    data: List[ErrorItem] = Field(
        ...,
        description="A list of ErrorItem objects.",
        example=[
            {
                "code": "invalid_request_error",
                "message": "The provided API key is invalid",
                "param": None,
                "line": None,
            }
        ],
    )


class ErrorInfo(OpenAIBaseModel):
    code: str = Field(..., description="The error code.", example="rate_limit_exceeded")
    message: str = Field(
        ...,
        description="A human-readable error message.",
        example="You have exceeded your API request quota",
    )
