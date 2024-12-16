from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"] = Field(
        description="The role of the message sender"
    )
    content: str = Field(description="The content of the message")
