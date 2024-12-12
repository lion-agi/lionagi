# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from lionagi.protocols.base import Observer

from .function_calling import FunctionCalling
from .tool import FuncTool, Tool


class ActionManager(Observer):

    def __init__(self, registry: dict | list = {}):
        """registry can be a dictionary of proper tool objects
        or a list of FuncTool objects"""
        super().__init__()
        self.registry = self._validate_registry(registry)

    def _validate_registry(self, value) -> dict[str, Tool]:
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
            "Registry must be a list or dictionary of Tool objects."
        )

    def register_tool(
        self, tool: FuncTool, update: bool = False, schema: dict = None
    ) -> None:
        if not isinstance(tool, Tool):
            tool = Tool(function=tool, schema_=schema)

        if tool.function_name in self.registry and not update:
            raise ValueError(
                f"Tool {tool.function_name} is already registered."
            )
        self.registry[tool.function_name] = tool

    def register_tools(
        self, tools: list[FuncTool] | FuncTool, update: bool = False
    ) -> None:
        """Register multiple tools.

        Args:
            tools: A single tool or list of tools (Tool objects or async callables).
            update: If True, allow overwriting existing tools.
        """
        if not isinstance(tools, list):
            tools = [tools]
        for t in tools:
            self.register_tool(t, update=update)

    async def invoke(
        self, function_name: str, arguments: dict[str, Any]
    ) -> FunctionCalling:
        """Invoke a registered tool asynchronously by its name.

        Args:
            function_name: The name of the tool (function) to invoke.
            arguments: A dictionary of arguments to pass to the tool function.

        Returns:
            The result of the async tool invocation.

        Raises:
            ValueError: If no tool is registered under the given function_name.
        """
        if function_name not in self.registry:
            raise ValueError(f"Function {function_name} is not registered.")
        tool = self.registry[function_name]
        action = FunctionCalling(_tool=tool, arguments=arguments)
        await action.invoke()
        return action

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """Return a list of schemas for all registered tools.

        If a tool does not have a schema, a minimal schema with the tool name is returned.

        Returns:
            A list of dictionaries representing schemas for each tool.
        """
        return [tool.schema_ for tool in self.registry.values()]

    def get_tool_schema(
        self, tools: bool | str | Tool | list[str | Tool] = False, /
    ) -> list | None:
        """Get schemas for specific tools or for all tools.

        Args:
            tools: If True, return schemas for all tools. If False, return empty dict.
                If a string or Tool is given, return schema for that tool.
                If a list is given, return schemas for all specified tools.
            **kwargs: Additional keyword arguments to include in the returned dictionary.

        Returns:
            A dictionary containing 'tools' key with schemas if requested, merged with kwargs.

        Raises:
            ValueError: If a specified tool is not registered.
        """
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
