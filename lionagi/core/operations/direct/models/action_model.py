from typing import Any

from lionfuncs import to_dict, validate_str
from pydantic import BaseModel, Field, field_validator


class ActionModel(BaseModel):

    title: str = Field(
        ...,
        title="Title",
        description="Provide a concise title summarizing the action.",
    )
    content: str = Field(
        ...,
        title="Content",
        description="Provide a brief description of the action to be performed.",
    )
    function: str = Field(
        ...,
        title="Function",
        description=(
            "Specify the name of the function to execute. **Choose from the provided "
            "`tool_schema`; do not invent function names.**"
        ),
        examples=["print", "add", "len"],
    )
    arguments: dict[str, Any] = Field(
        {},
        title="Arguments",
        description=(
            "Provide the arguments to pass to the function as a dictionary. **Use "
            "argument names and types as specified in the `tool_schema`; do not "
            "invent argument names.**"
        ),
        examples=[{"num1": 1, "num2": 2}, {"x": "hello", "y": "world"}],
    )

    @field_validator("title", mode="before")
    def validate_title(cls, value: Any) -> str:
        return validate_str(value, "title")

    @field_validator("content", mode="before")
    def validate_content(cls, value: Any) -> str:
        return validate_str(value, "content")

    @field_validator("function", mode="before")
    def validate_function(cls, value: Any) -> str:
        return validate_str(value, "function")

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            suppress=True,
            recursive=True,
        )


__all__ = ["ActionModel"]
