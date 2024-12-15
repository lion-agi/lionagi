# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
from typing import Any

from pydantic import Field, PrivateAttr, ValidationError, field_serializer

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

    def _validate_arguments(self) -> None:
        """Validate arguments against tool schema."""
        if not self._tool.schema_:
            return

        schema = self._tool.schema_
        if "parameters" not in schema:
            return

        params_schema = schema["parameters"]
        required = params_schema.get("required", [])
        properties = params_schema.get("properties", {})

        # Check required parameters
        for param in required:
            if param not in self.arguments:
                raise ValueError(f"Missing required parameter: {param}")

        # Validate parameter types
        for param, value in self.arguments.items():
            if param not in properties:
                raise ValueError(f"Unknown parameter: {param}")

            param_schema = properties[param]
            param_type = param_schema.get("type")

            # Basic type validation
            if param_type == "string" and not isinstance(value, str):
                raise ValueError(f"Parameter {param} must be a string")
            elif param_type == "number" and not isinstance(
                value, (int, float)
            ):
                raise ValueError(f"Parameter {param} must be a number")
            elif param_type == "integer" and not isinstance(value, int):
                raise ValueError(f"Parameter {param} must be an integer")
            elif param_type == "boolean" and not isinstance(value, bool):
                raise ValueError(f"Parameter {param} must be a boolean")
            elif param_type == "array" and not isinstance(value, list):
                raise ValueError(f"Parameter {param} must be an array")
            elif param_type == "object" and not isinstance(value, dict):
                raise ValueError(f"Parameter {param} must be an object")

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

            # Validate arguments before execution
            self._validate_arguments()

            res = await self._tool.tcall.function(**self.arguments)
            self.execution_time = asyncio.get_event_loop().time() - start
            self.execution_result = res
            self.status = EventStatus.COMPLETED

        except (ValueError, ValidationError) as e:
            self.execution_time = asyncio.get_event_loop().time() - start
            self.error = str(e)
            self.status = EventStatus.FAILED
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
