# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import ClassVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    field_serializer,
    field_validator,
    model_validator,
)

from lionagi.operatives.action.tool import Tool
from lionagi.protocols.graph.node import Node


class LionTool(ABC):
    is_lion_system_tool: bool = True
    system_tool_name: str

    @abstractmethod
    def to_tool(self) -> Tool:
        pass


class Prompt(Resource):
    category: ResourceCategory = Field(
        default=ResourceCategory.PROMPT, frozen=True
    )


class DocumentMeta(BaseModel):

    url: str | None = None
    file_path: str | Path | None = None
    from_url: bool | None = None

    pass
