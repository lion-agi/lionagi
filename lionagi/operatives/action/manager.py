# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines the `ActionManager` class, a specialized Manager that registers
`Tool` objects (or callables) for function invocation. It can match
incoming requests (ActionRequest) to a registered tool, then run it.
"""

from typing import Any

from lionagi.protocols._concepts import Manager
from lionagi.protocols.generic.event import Execution
from lionagi.protocols.messages.action_request import ActionRequest
from lionagi.utils import to_list

from .function_calling import FunctionCalling
from .request_response_model import ActionRequestModel
from .tool import FuncTool, FuncToolRef, Tool, ToolRef

__all__ = ("ActionManager",)


class ActionManager(Manager):
    """
    A manager that registers function-based tools and invokes them
    when triggered by an ActionRequest. Tools can be registered
    individually or in bulk, and each tool must have a unique name.
    """

    def __init__(self, *args: FuncTool, **kwargs) -> None:
        """
        Create an ActionManager, optionally registering initial tools.

        Args:
            *args (FuncTool):
                A variable number of tools or callables.
            **kwargs:
                Additional named arguments that are also considered tools.
        """
        super().__init__()
        self.registry: dict[str, Tool] = {}

        tools = []
        if args:
            tools.extend(to_list(args, dropna=True, flatten=True))
        if kwargs:
            tools.extend(to_list(kwargs.values(), dropna=True, flatten=True))

        self.register_tools(tools, update=True)

    def __contains__(self, tool: FuncToolRef) -> bool:
        """
        Check if a tool is registered, by either:
        - The Tool object itself,
        - A string name for the function,
        - Or the callable's __name__.

        Returns:
            bool: True if found, else False.
        """
        if isinstance(tool, Tool):
            return tool.function in self.registry
        elif isinstance(tool, str):
            return tool in self.registry
        elif callable(tool):
            return tool.__name__ in self.registry
        return False

    def register_tool(self, tool: FuncTool, update: bool = False) -> None:
        """
        Register a single tool/callable in the manager.

        Args:
            tool (FuncTool):
                A `Tool` object or a raw callable function.
            update (bool):
                If True, allow replacing an existing tool with the same name.

        Raises:
            ValueError: If tool already registered and update=False.
            TypeError: If `tool` is not a Tool or callable.
        """
        # Check if tool already exists
        if not update and tool in self:
            name = None
            if isinstance(tool, Tool):
                name = tool.function
            elif callable(tool):
                name = tool.__name__
            raise ValueError(f"Tool {name} is already registered.")

        # Convert raw callable to a Tool if needed
        if callable(tool):
            tool = Tool(func_callable=tool)
        if not isinstance(tool, Tool):
            raise TypeError(
                "Must provide a `Tool` object or a callable function."
            )
        self.registry[tool.function] = tool

    def register_tools(
        self, tools: list[FuncTool] | FuncTool, update: bool = False
    ) -> None:
        """
        Register multiple tools at once.

        Args:
            tools (list[FuncTool] | FuncTool):
                A single or list of tools/callables.
            update (bool):
                If True, allow updating existing tools.

        Raises:
            ValueError: If a duplicate tool is found and update=False.
            TypeError: If any item is not a Tool or callable.
        """
        tools_list = tools if isinstance(tools, list) else [tools]
        for t in tools_list:
            self.register_tool(t, update=update)

    def match_tool(
        self, action_request: ActionRequest | ActionRequestModel | dict
    ) -> FunctionCalling:
        """
        Convert an ActionRequest (or dict with "function"/"arguments")
        into a `FunctionCalling` instance by finding the matching tool.

        Raises:
            TypeError: If `action_request` is an unsupported type.
            ValueError: If no matching tool is found in the registry.

        Returns:
            FunctionCalling: The event object that can be invoked.
        """
        if not isinstance(
            action_request, ActionRequest | ActionRequestModel | dict
        ):
            raise TypeError(f"Unsupported type {type(action_request)}")

        func, args = None, None
        if isinstance(action_request, dict):
            func = action_request["function"]
            args = action_request["arguments"]
        else:
            func = action_request.function
            args = action_request.arguments

        tool = self.registry.get(func, None)
        if not isinstance(tool, Tool):
            raise ValueError(f"Function {func} is not registered.")

        return FunctionCalling(func_tool=tool, arguments=args)

    async def invoke(
        self,
        func_call: ActionRequestModel | ActionRequest,
    ) -> FunctionCalling:
        """
        High-level API to parse and run a function call.

        Steps:
          1) Convert `func_call` to FunctionCalling via `match_tool`.
          2) `invoke()` the resulting object.
          3) Return the `FunctionCalling`, which includes `execution`.

        Args:
            func_call: The action request model or ActionRequest object.

        Returns:
            `FunctionCalling` event after it completes execution.
        """
        function_calling = self.match_tool(func_call)
        await function_calling.invoke()
        return function_calling

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """Return the list of JSON schemas for all registered tools."""
        return [tool.tool_schema for tool in self.registry.values()]

    def get_tool_schema(
        self,
        tools: ToolRef = False,
        auto_register: bool = True,
        update: bool = False,
    ) -> dict:
        """
        Retrieve schemas for a subset of tools or for all.

        Args:
            tools (ToolRef):
                - If True, return schema for all tools.
                - If False, return an empty dict.
                - If specific tool(s), returns only those schemas.
            auto_register (bool):
                If a tool (callable) is not yet in the registry, register if True.
            update (bool):
                If True, allow updating existing tools.

        Returns:
            dict: e.g., {"tools": [list of schemas]}

        Raises:
            ValueError: If requested tool is not found and auto_register=False.
            TypeError: If tool specification is invalid.
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
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """
        Internal helper to handle retrieval or registration of a single or
        multiple tools, returning their schema(s).
        """
        if isinstance(tool, dict):
            return tool  # Already a schema
        if callable(tool):
            # Possibly unregistered function
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

# File: lionagi/operatives/action/manager.py
