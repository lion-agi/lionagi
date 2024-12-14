# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence
from typing import Any, TypeAlias

from lionagi.protocols.base import Manager

from .function_calling import FunctionCalling
from .tool import FuncTool, Tool

# Type aliases
ToolName: TypeAlias = str
ToolInput: TypeAlias = FuncTool | Sequence[FuncTool]
ToolRegistry: TypeAlias = dict[str, Tool] | Sequence[Tool]
ToolSpecifier: TypeAlias = bool | ToolName | Tool | Sequence[ToolName | Tool]
Schema: TypeAlias = dict[str, Any]


__all__ = ("ActionManager",)


class ActionManager(Manager):
    """Manages tool registration, validation, and asynchronous invocation.

    Handles registration and execution of tools while maintaining a validated
    registry. Supports both individual and batch tool operations with schema
    management.
    """

    def __init__(self, registry: ToolRegistry = {}) -> None:
        """Initialize with optional tool registry."""
        super().__init__()
        self.registry: dict[ToolName, Tool] = self._validate_registry(registry)

    def _validate_registry(self, value: ToolRegistry) -> dict[ToolName, Tool]:
        """Validate and normalize registry input."""
        if not value:
            return {}

        if isinstance(value, list):
            if not all(isinstance(v, Tool) for v in value):
                raise ValueError("All items in registry must be Tool objects.")
            return {t.function_name: t for t in value}

        if isinstance(value, dict):
            if not all(isinstance(v, Tool) for v in value.values()):
                raise ValueError(
                    "All values in registry must be Tool objects."
                )
            return value

        raise ValueError(
            "Registry must be a sequence or dictionary of Tool objects."
        )

    def register_tool(
        self,
        tool: FuncTool,
        *,
        update: bool = False,
        schema: Schema | None = None,
    ) -> None:
        """Register a single tool with optional schema."""
        if not isinstance(tool, Tool):
            tool = Tool(function=tool, schema_=schema)

        if tool.function_name in self.registry and not update:
            raise ValueError(
                f"Tool {tool.function_name} is already registered."
            )
        self.registry[tool.function_name] = tool

    def register_tools(
        self, tools: ToolInput, *, update: bool = False
    ) -> None:
        """Register multiple tools simultaneously."""
        if not isinstance(tools, list):
            tools = [tools]
        for t in tools:
            self.register_tool(t, update=update)

    async def invoke(
        self, function_name: ToolName, arguments: dict[str, Any]
    ) -> FunctionCalling:
        """Invoke registered tool asynchronously."""
        if function_name not in self.registry:
            raise ValueError(f"Function {function_name} is not registered.")
        tool = self.registry[function_name]
        action = FunctionCalling(_tool=tool, arguments=arguments)
        await action.invoke()
        return action

    @property
    def schema_list(self) -> list[Schema]:
        """Get schemas for all registered tools."""
        return [tool.schema_ for tool in self.registry.values()]

    def get_tool_schema(
        self, tools: ToolSpecifier = False
    ) -> list[Schema] | None:
        """Get schemas for specified tools."""
        if tools is True:
            return self.schema_list
        elif tools is False:
            return None

        # Normalize tools to a list
        if not isinstance(tools, list):
            tools = [tools]

        schemas: list[dict[str, Any]] = []
        for t in tools:
            name = t.function_name if isinstance(t, Tool) else t
            if isinstance(name, str) and name in self.registry:
                schemas.append(self.registry[name].schema_)
            else:
                raise ValueError(f"Tool {name} is not registered.")
        return schemas


# File: lion/protocols/action.py
