# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from pydantic import BaseModel, Field


class TextContent(BaseModel):
    type: Literal["text"] = Field(description="Type of content block")
    text: str = Field(description="The text content")


class ToolUseContent(BaseModel):
    type: Literal["tool_use"] = Field(description="Type of content block")
    id: str = Field(description="Unique identifier for this tool use")
    name: str = Field(description="Name of the tool being called")
    input: dict = Field(description="Input parameters for the tool call")


class ToolResultContent(BaseModel):
    type: Literal["tool_result"] = Field(description="Type of content block")
    tool_use_id: str = Field(
        description="ID of the tool use this is a result for"
    )
    content: str = Field(
        description="The result content from running the tool"
    )


ContentBlock = TextContent | ToolUseContent | ToolResultContent
