from typing import Literal

from pydantic import BaseModel, Field


class Function(BaseModel):
    name: str = Field(description="The name of the function to call.")
    arguments: str = Field(
        description="The arguments to pass to the function."
    )


class ToolCall(BaseModel):
    id: str = Field(description="The ID of the tool call.")
    type: Literal["function"] = Field(description="The type of the tool call.")
    function: Function = Field(description="The function call details.")
