# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: Role = Field(
        description="The role of the message, either 'system', 'user', 'assistant', or 'tool'"
    )

    content: str = Field(description="The content of the message")

    images: list[str] | None = Field(
        None,
        description="a list of images to include in the message (for multimodal models such as 'llava')",
    )

    tool_calls: list | None = Field(
        None, description="a list of tools the model wants to use"
    )
