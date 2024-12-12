# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import Any, Self

from pydantic import PrivateAttr, field_serializer, model_validator

from ..protocols.base import EventStatus, IDType
from .base import Action
from .tool import Tool


class FunctionCalling(Action):

    _tool: Tool = PrivateAttr()
    arguments: dict[str, Any]
    tool_id: IDType | None = None

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        self.tool_id = self._tool.id

    @field_serializer("tool_id")
    def _serialize_tool_id(self, value: IDType) -> str:
        return str(value)

    async def invoke(self):
        start = asyncio.get_event_loop().time()
        self.status = EventStatus.IN_PROGRESS
        try:
            res = await self._tool.tcall(**self.arguments)
            self.execution_time = start - asyncio.get_event_loop().time()
            self.execution_result = res
            self.status = EventStatus.COMPLETED
        except Exception as e:
            self.execution_time = start - asyncio.get_event_loop().time()
            self.error = str(e)
            self.status = EventStatus.FAILED
