# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import Any

from pydantic import Field, PrivateAttr, field_serializer

from ..protocols.base import EventStatus, IDType
from .base import Action
from .tool import Tool

__all__ = ("FunctionCalling",)


class FunctionCalling(Action):
    """Handles asynchronous function calling with execution tracking.

    Manages tool invocation, execution timing, and error handling while
    maintaining state through Pydantic validation.
    """

    _tool: Tool = PrivateAttr()
    arguments: dict[str, Any]
    tool_id: IDType | None = Field(
        default=None, description="ID of the tool being called"
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True,
        "use_enum_values": False,
    }

    @classmethod
    def create(
        cls, tool: Tool, arguments: dict[str, Any]
    ) -> "FunctionCalling":
        """Create a new FunctionCalling instance.

        Args:
            tool: Tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            New FunctionCalling instance
        """
        instance = cls(arguments=arguments)
        object.__setattr__(instance, "_tool", tool)
        instance.tool_id = tool.id
        return instance

    @field_serializer("tool_id")
    def _serialize_tool_id(self, value: IDType) -> str:
        """Serialize tool ID to string format."""
        return str(value)

    async def invoke(self) -> None:
        """Execute tool function with timing and error tracking.

        Updates status and tracks execution time while handling any errors
        that occur during tool invocation.
        """
        start = asyncio.get_event_loop().time()
        self.status = EventStatus.PROCESSING

        try:
            if not hasattr(self, "_tool"):
                raise ValueError("Tool not initialized")

            if not self._tool.tcall:
                raise ValueError("Tool call parameters not initialized")

            if not self._tool.tcall.function:
                raise ValueError("Tool function not initialized")

            res = await self._tool.tcall.function(**self.arguments)
            self.execution_time = asyncio.get_event_loop().time() - start
            self.execution_result = res
            self.status = EventStatus.COMPLETED

        except Exception as e:
            self.execution_time = asyncio.get_event_loop().time() - start
            self.error = str(e)
            self.status = EventStatus.FAILED

    def __repr__(self) -> str:
        """Returns a string representation of the FunctionCalling instance."""
        return (
            f"FunctionCalling(tool_id={self.tool_id}, "
            f"status={self.status.name}, "
            f"execution_time={self.execution_time})"
        )
