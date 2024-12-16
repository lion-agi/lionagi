# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from functools import singledispatchmethod

from lionagi.core.communication.action_request import ActionRequest
from lionagi.core.generic.log_manager import LogManager
from lionagi.core.typing import Any, Callable
from lionagi.libs.parse.types import to_dict, to_list
from lionagi.protocols.operatives.action import ActionRequestModel

from .function_calling import FunctionCalling
from .tool import Tool, func_to_tool

# Type definitions for tool registration and lookup
FUNCTOOL = Tool | Callable[..., Any]
FINDABLE_TOOL = FUNCTOOL | str
INPUTTABLE_TOOL = dict[str, Any] | bool | FINDABLE_TOOL
TOOL_TYPE = FINDABLE_TOOL | list[FINDABLE_TOOL] | INPUTTABLE_TOOL


class ActionManager:
    """Manages registration and execution of tools.

    The ActionManager serves as a central registry for tools, providing:
    1. Tool registration and management
    2. Function call matching to registered tools
    3. Tool invocation with argument handling
    4. Logging of tool execution

    Tools can be registered either as Tool objects or as callable functions
    (which are automatically converted to Tool objects). The manager supports
    various formats for function calls and provides comprehensive logging
    of tool execution.

    Attributes:
        registry (dict[str, Tool]): Dictionary mapping tool names to Tool objects.
        logger (LogManager): Logger for tracking tool execution.
    """

    def __init__(
        self, registry: dict[str, Tool] | None = None, logger=None
    ) -> None:
        """Initialize the ActionManager instance.

        Args:
            registry: Optional dictionary of pre-registered tools.
                Keys are tool names, values are Tool objects.
            logger: Optional logger for tracking tool execution.
                If None, creates a new LogManager instance.
        """
        self.registry: dict[str, Tool] = registry or {}
        self.logger = logger or LogManager()

    def __contains__(self, tool: FINDABLE_TOOL) -> bool:
        """Check if a tool is registered in the registry.

        Supports checking by:
        - Tool object
        - Tool name (string)
        - Callable function

        Args:
            tool: The tool to check for registration.

        Returns:
            bool: True if tool is registered, False otherwise.
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

        If the tool is a callable function, it is automatically converted
        to a Tool object. Existing tools can be updated if update=True.

        Args:
            tool: The tool to register (Tool object or callable).
            update: If True, update existing tool; if False, raise error.

        Raises:
            ValueError: If tool already registered and update=False.
            TypeError: If tool is not a Tool object or callable.
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

        Handles both single tools and lists of tools. Each tool can be
        either a Tool object or a callable function.

        Args:
            tools: Single tool or list of tools to register.
            update: If True, update existing tools; if False, raise error.

        Raises:
            ValueError: If any tool is already registered.
            TypeError: If any tool is not a Tool object or callable.
        """
        tools_list = tools if isinstance(tools, list) else [tools]
        [
            self.register_tool(tool, update=update)
            for tool in to_list(tools_list, dropna=True, flatten=True)
        ]

    @singledispatchmethod
    def match_tool(self, func_call: Any) -> FunctionCalling:
        """Match a function call to a registered tool.

        This is a single dispatch method that handles different function
        call formats. The base method handles unsupported types.

        Args:
            func_call: The function call specification.

        Raises:
            TypeError: If input type is not supported.
        """
        raise TypeError(f"Unsupported type {type(func_call)}")

    @match_tool.register
    def _(self, func_call: tuple) -> FunctionCalling:
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
        tool = self.registry.get(func_call.function)
        if not tool:
            func_ = func_call.function
            raise ValueError(f"Function {func_} is not registered.")
        return FunctionCalling(func_tool=tool, arguments=func_call.arguments)

    @match_tool.register
    def _(self, func_call: str) -> FunctionCalling:
        _call = None
        try:
            _call = to_dict(func_call, str_type="json", fuzzy_parse=True)
        except Exception as e:
            raise ValueError(f"Invalid function call {func_call}") from e

        if isinstance(_call, dict):
            return self.match_tool(_call)
        raise ValueError(f"Invalid function call {func_call}")

    async def invoke(self, func_call: dict | str | ActionRequest) -> Any:
        """Invoke a tool based on the provided function call.

        1. Matches function call to registered tool
        2. Creates FunctionCalling instance
        3. Invokes function with arguments
        4. Logs execution details
        5. Returns result

        Args:
            func_call: Function call specification in supported format.
            log_manager: Optional logger for execution tracking.

        Returns:
            Result of tool invocation after processing pipeline.

        Raises:
            ValueError: If function not registered or call format invalid.
        """
        function_calling = self.match_tool(func_call)
        result = await function_calling.invoke()
        await self.logger.alog(function_calling.to_log())
        return result

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """List all tool schemas currently registered.

        Returns:
            List of OpenAI function schemas for all registered tools.
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
            Dictionary containing tool schemas and additional kwargs.

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
