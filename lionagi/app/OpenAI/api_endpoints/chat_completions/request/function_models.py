# File: function_models.py
from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class FunctionParameters(BaseModel):
    type: Literal["object"] = "object"
    properties: Dict[str, Dict[str, Any]]
    required: List[str] | None = None


class FunctionDefinition(BaseModel):
    name: Annotated[
        str,
        Field(
            max_length=64,
            pattern="^[a-zA-Z0-9_-]+$",
            description=(
                "The name of the function to be called. Must be a-z, A-Z, 0-9, "
                "or contain underscores and dashes, with a maximum length of 64."
            ),
        ),
    ]
    description: str | None = Field(
        None,
        description=(
            "A description of what the function does, used by the model to "
            "choose when and how to call the function."
        ),
    )
    parameters: FunctionParameters | None = Field(
        None,
        description=(
            "The parameters the functions accepts, described as a JSON Schema "
            "object. See the guide for examples, and the JSON Schema "
            "reference for documentation about the format."
        ),
    )


class Tool(BaseModel):
    type: Literal["function"] = Field(
        description="The type of the tool. Currently, only function is supported."
    )
    function: FunctionDefinition = Field(description="The function definition.")
    strict: bool | None = Field(
        False,
        description=(
            "Whether to enable strict schema adherence when generating the "
            "function call. If set to true, the model will follow the exact "
            "schema defined in the parameters field."
        ),
    )


class ToolChoice(BaseModel):
    type: Literal["function"] = Field(
        description="The type of the tool. Currently, only function is supported."
    )
    function: Dict[str, str] = Field(description="Specifies the function to be called.")
