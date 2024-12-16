# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from functools import singledispatchmethod
from typing import Any

from lionagi.fields.action import ActionRequestModel
from lionagi.libs.parse.types import to_dict
from lionagi.messages.types import ActionRequest
from lionagi.protocols.types import LogManager, Manager
from lionagi.utils import to_list

from .function_calling import FunctionCalling
from .tool import Tool, func_to_tool

FUNCTOOL = Tool | Callable[..., Any]
FINDABLE_TOOL = FUNCTOOL | str
INPUTTABLE_TOOL = dict[str, Any] | bool | FINDABLE_TOOL
TOOL_TYPE = FINDABLE_TOOL | list[FINDABLE_TOOL] | INPUTTABLE_TOOL


class ActionManager(Manager):
    """
    Manages tools in the system.

    Responsible for managing a registry of tools, which can be functions or
    callable objects. Provides methods to register tools, match function
    calls to tools, and invoke tools asynchronously.

    Attributes:
        registry: Mapping of tool names to Tool objects.
    """

    def __init__(self, registry: dict[str, Tool] | None = None) -> None:
        """Initialize the ToolManager instance.

        Args:
            registry: Optional dictionary of pre-registered tools.
                      Keys are tool names, values are Tool objects.
        """
        self.registry: dict[str, Tool] = registry or {}

    def __contains__(self, tool: FINDABLE_TOOL) -> bool:
        """Check if a tool is registered in the registry.

        Args:
            tool: The tool to check. Can be a Tool object, a string
                  (tool name), or a callable.

        Returns:
            True if the tool is registered, False otherwise.
        """
        if isinstance(tool, Tool):
            return tool.function_name in self.registry
        elif isinstance(tool, str):
            return tool in self.registry
        elif callable(tool):
            return tool.__name__ in self.registry
        return False

    def register_tool(
        self,
        tool: FUNCTOOL,
        update: bool = False,
    ) -> None:
        """Register a single tool in the registry.

        Args:
            tool: The tool to register. Can be a Tool object or a callable.
            update: If True, update the tool if it's already registered.
                    If False, raise an error if already registered.

        Raises:
            ValueError: If tool is already registered and update is False.
            TypeError: If the provided tool is not a Tool object or callable.
        """
        if not update and tool in self:
            name = None
            if isinstance(tool, Tool):
                name = tool.function_name
            elif callable(tool):
                name = tool.__name__
            raise ValueError(f"Tool {name} is already registered.")

        if callable(tool):
            tool = func_to_tool(tool)[0]
        if not isinstance(tool, Tool):
            raise TypeError("Please register a Tool object or callable.")

        self.registry[tool.function_name] = tool

    def register_tools(
        self,
        tools: list[FUNCTOOL] | FUNCTOOL,
        update: bool = False,
    ) -> None:
        """Register multiple tools in the registry.

        Args:
            tools: A single tool or a list of tools to register.
                   Each tool can be a Tool object or a callable.

        Raises:
            ValueError: If any tool is already registered.
            TypeError: If any provided tool is not a Tool object or callable.
        """
        tools_list = tools if isinstance(tools, list) else [tools]
        [
            self.register_tool(tool, update=update)
            for tool in to_list(tools_list, dropna=True, flatten=True)
        ]

    @singledispatchmethod
    def match_tool(self, func_call: Any) -> FunctionCalling:
        """Match a function call to a registered tool.

        This method uses single dispatch to handle different input types.

        Args:
            func_call: The function call to match. Can be a tuple, dict,
                       ActionRequest, or string.

        Returns:
            A FunctionCalling object representing the matched tool.

        Raises:
            TypeError: If the input type is not supported.
            ValueError: If function is not registered or call format invalid.
        """
        raise TypeError(f"Unsupported type {type(func_call)}")

    @match_tool.register
    def _(self, func_call: tuple) -> FunctionCalling:
        """Match a function call tuple to a registered tool."""
        if len(func_call) == 2:
            function_name = func_call[0]
            arguments = func_call[1]
            tool = self.registry.get(function_name)
            if not tool:
                raise ValueError(f"Function {function_name} is not registered")
            return FunctionCalling(func_tool=tool, arguments=arguments)
        else:
            raise ValueError(f"Invalid function call {func_call}")

    @match_tool.register
    def _(self, func_call: dict) -> FunctionCalling:
        """Match a function call dictionary to a registered tool."""
        if len(func_call) == 2 and (
            {
                "function",
                "arguments",
            }
            <= func_call.keys()
        ):
            function_name = func_call["function"]
            tool = self.registry.get(function_name)
            if not tool:
                raise ValueError(f"Function {function_name} is not registered")
            return FunctionCalling(
                func_tool=tool,
                arguments=func_call["arguments"],
            )
        raise ValueError(f"Invalid function call {func_call}")

    @match_tool.register
    def _(
        self, func_call: ActionRequest | ActionRequestModel
    ) -> FunctionCalling:
        """Match an ActionRequest to a registered tool."""
        tool = self.registry.get(func_call.function)
        if not tool:
            func_ = func_call.function
            raise ValueError(f"Function {func_} is not registered.")
        return FunctionCalling(func_tool=tool, arguments=func_call.arguments)

    @match_tool.register
    def _(self, func_call: str) -> FunctionCalling:
        """Parse a string and match it to a registered tool."""
        _call = None
        try:
            _call = to_dict(func_call, str_type="json", fuzzy_parse=True)
        except Exception as e:
            raise ValueError(f"Invalid function call {func_call}") from e

        if isinstance(_call, dict):
            return self.match_tool(_call)
        raise ValueError(f"Invalid function call {func_call}")

    async def invoke(
        self,
        func_call: dict | str | ActionRequest,
        log_manager: LogManager = None,
    ) -> Any:
        """Invoke a tool based on the provided function call.

        Args:
            func_call: The function call to invoke. Can be a dictionary,
                       string, or ActionRequest object.

        Returns:
            The result of invoking the matched tool.

        Raises:
            ValueError: If function call can't be matched to registered tool.
        """
        function_calling = self.match_tool(func_call)
        result = await function_calling.invoke()
        if log_manager is not None:
            await log_manager.alog(function_calling.to_log())
        return result

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """List all tool schemas currently registered in the ToolManager.

        Returns:
            A list of schema dictionaries for all registered tools.
        """
        return [tool.schema_ for tool in self.registry.values()]

    def get_tool_schema(
        self,
        tools: TOOL_TYPE = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Retrieve the schema for specific tools or all tools.

        Args:
            tools: Specification of which tools to retrieve schemas for.
                   If True, return all tools. If False, return empty dict.
                   Can also be a specific tool or list of tools.
            **kwargs: Additional keyword arguments to include in output.

        Returns:
            A dictionary containing tool schemas and additional kwargs.

        Raises:
            ValueError: If a specified tool is not registered.
            TypeError: If an unsupported tool type is provided.
        """
        if isinstance(tools, bool):
            if tools:
                tool_kwarg = {"tools": self.schema_list}
            else:
                tool_kwarg = {}
        else:
            tool_kwarg = {"tools": self._get_tool_schema(tools)}
        return tool_kwarg | kwargs

    def _get_tool_schema(
        self,
        tool: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Retrieve the schema for a specific tool."""
        if isinstance(tool, dict):
            return tool
        if isinstance(tool, Callable):
            name = tool.__name__
            if name in self.registry:
                return self.registry[name].schema_
            raise ValueError(f"Tool {name} is not registered.")

        elif isinstance(tool, Tool) or isinstance(tool, str):
            name = tool.function_name if isinstance(tool, Tool) else tool
            if name in self.registry:
                return self.registry[name].schema_
            raise ValueError(f"Tool {name} is not registered.")
        elif isinstance(tool, list):
            return [self._get_tool_schema(t) for t in tool]
        raise TypeError(f"Unsupported type {type(tool)}")


__all__ = ["ActionManager"]
# File: lion_core/action/tool_manager.py
