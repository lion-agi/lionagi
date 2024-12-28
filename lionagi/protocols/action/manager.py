# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from collections.abc import Callable
from typing import Any

from lionagi.protocols.generic.event import Execution
from lionagi.utils import EventStatus, to_list

from ..generic.log import LogManager
from ..messages.action_request import ActionRequest
from .function_calling import FunctionCalling
from .request_response_model import ActionRequestModel
from .tool import FuncTool, FuncToolRef, Tool, ToolRef

__all__ = ("ActionManager",)


class ActionManager:

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

    def __contains__(self, tool: FuncToolRef) -> bool:
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
            return tool.function in self.registry
        elif isinstance(tool, str):
            return tool in self.registry
        elif callable(tool):
            return tool.__name__ in self.registry
        return False

    def register_tool(
        self,
        tool: FuncTool,
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
                name = tool.function
            elif callable(tool):
                name = tool.__name__
            raise ValueError(f"Tool {name} is already registered.")

        if callable(tool):
            tool = Tool(func_callable=tool)
        if not isinstance(tool, Tool):
            raise TypeError("Please register a Tool object or callable.")

        self.registry[tool.function] = tool

    def register_tools(
        self,
        tools: list[FuncTool] | FuncTool,
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

    def match_tool(
        self, action_request: ActionRequest | ActionRequestModel
    ) -> FunctionCalling:
        if not isinstance(action_request, ActionRequest | ActionRequestModel):
            raise TypeError(f"Unsupported type {type(action_request)}")

        tool = self.registry.get(action_request.function, None)
        if not tool:
            raise ValueError(
                f"Function {action_request.function} is not registered."
            )
        return

    async def invoke(
        self, func_call: ActionRequestModel | ActionRequest
    ) -> Execution:
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
        try:
            function_calling = self.match_tool(func_call)
        except ValueError as e:
            return Execution(
                status=EventStatus.FAILED,
                error=str(e),
                result=None,
            )

        await function_calling.invoke()
        await self.logger.alog(function_calling.to_log())
        return function_calling.execution

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """List all tool schemas currently registered.

        Returns:
            List of OpenAI function schemas for all registered tools.
        """
        return [tool.tool_schema for tool in self.registry.values()]

    def get_tool_schema(self, tools: ToolRef = False) -> list[dict]:
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
        if isinstance(tools, list | tuple) and len(tools) == 1:
            tools = tools[0]
        if isinstance(tools, bool):
            if tools is True:
                return self.schema_list
            return []
        else:
            return self._get_tool_schema(tools)

    def _get_tool_schema(
        self,
        tool: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if isinstance(tool, dict):
            return tool
        if isinstance(tool, Callable):
            name = tool.__name__
            if name in self.registry:
                return self.registry[name].tool_schema
            raise ValueError(f"Tool {name} is not registered.")

        elif isinstance(tool, Tool) or isinstance(tool, str):
            name = tool.function if isinstance(tool, Tool) else tool
            if name in self.registry:
                return self.registry[name].tool_schema
            raise ValueError(f"Tool {name} is not registered.")
        elif isinstance(tool, list):
            return [self._get_tool_schema(t) for t in tool]
        raise TypeError(f"Unsupported type {type(tool)}")


__all__ = ["ActionManager"]
