# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from lionagi.protocols._concepts import Manager
from lionagi.protocols.generic.event import EventStatus, Execution
from lionagi.protocols.generic.log import Log
from lionagi.protocols.messages.action_request import ActionRequest
from lionagi.utils import to_list

from .function_calling import FunctionCalling
from .request_response_model import ActionRequestModel
from .tool import FuncTool, FuncToolRef, Tool, ToolRef

__all__ = ("ActionManager",)


class ActionManager(Manager):

    def __init__(self, *args: FuncTool, **kwargs) -> None:

        super().__init__()
        self.registry: dict[str, Tool] = {}

        tools = []
        if args:
            tools.extend(to_list(args, dropna=True, flatten=True))
        if kwargs:
            tools.extend(
                to_list(kwargs, dropna=True, flatten=True, use_values=True)
            )
        self.register_tools(tools, update=True)

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
        if not isinstance(tool, Tool):
            raise ValueError(
                f"Function {action_request.function} is not registered."
            )
        return FunctionCalling(
            func_tool=tool, arguments=action_request.arguments
        )

    async def invoke(
        self, func_call: ActionRequestModel | ActionRequest
    ) -> FunctionCalling | Execution | None:
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
            return Log(
                content={
                    "event_type": "function_call",
                    "status": EventStatus.FAILED,
                    "error": str(e),
                }
            )
        await function_calling.invoke()
        return function_calling

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """List all tool schemas currently registered.

        Returns:
            List of OpenAI function schemas for all registered tools.
        """
        return [tool.tool_schema for tool in self.registry.values()]

    def get_tool_schema(
        self,
        tools: ToolRef = False,
        auto_register: bool = True,
        update: bool = False,
    ) -> dict:
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
                return {"tools": self.schema_list}
            return []
        else:
            schemas = self._get_tool_schema(
                tools, auto_register=auto_register, update=update
            )
            return {"tools": schemas}

    def _get_tool_schema(
        self,
        tool: Any,
        auto_register: bool = True,
        update: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if isinstance(tool, dict):
            return tool
        if callable(tool):
            name = tool.__name__
            if name not in self.registry:
                if auto_register:
                    self.register_tool(tool, update=update)
                else:
                    raise ValueError(f"Tool {name} is not registered.")
            return self.registry[name].tool_schema

        elif isinstance(tool, Tool) or isinstance(tool, str):
            name = tool.function if isinstance(tool, Tool) else tool
            if name in self.registry:
                return self.registry[name].tool_schema
            raise ValueError(f"Tool {name} is not registered.")
        elif isinstance(tool, list):
            return [
                self._get_tool_schema(t, auto_register=auto_register)
                for t in tool
            ]
        raise TypeError(f"Unsupported type {type(tool)}")


__all__ = ["ActionManager"]
