from typing import Any
from pydantic import BaseModel, Field


class OperationGuide(BaseModel):
    name: str = Field(..., title="Operation Name")
    assignment: str = Field(..., title="Operation Assignment")
    thinking_style: str | dict[str, Any] | None = Field(
        None, title="Operation Thinking Style"
    )
    instruction: str | dict | None = Field(None, title="Operation Instruction")
    guidance: str | dict | None = Field(None, title="Operation Guidance")
    version: str = Field(None, title="Operation Version")
    metadata: dict = {}
