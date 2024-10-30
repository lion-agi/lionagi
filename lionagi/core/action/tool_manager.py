import inspect
from collections.abc import Callable
from functools import singledispatchmethod
from typing import Any, List, Tuple, Union

from lionfuncs import function_to_schema, lcall, to_dict, to_list

from lionagi.core.action.function_calling import FunctionCalling
from lionagi.core.action.tool import TOOL_TYPE, Tool
from lionagi.core.collections.abc import Actionable


class ToolManager(Actionable):
    """
    Manages tools in the system. Provides functionality to register tools,
    invoke them based on various input formats, and retrieve tool schemas.
    """

    def __init__(self, registry: dict[str, Tool] = None) -> None:
        """
        Initializes a new instance of ToolManager.

        Args:
            registry (dict[str, Tool], optional): A dictionary to store registered tools.
                Defaults to an empty dictionary.
        """
        self.registry = registry or {}

    def __contains__(self, tool) -> bool:
        if isinstance(tool, Tool):
            return tool.name in self.registry

        elif isinstance(tool, str):
            return tool in self.registry

        elif inspect.isfunction(tool):
            return tool.__name__ in self.registry

        return False

    def _register_tool(
        self, tool: Tool | Callable, update: bool = False
    ) -> bool:
        """
        Registers a single tool or multiple tools based on the input type.

        Args:
            tool (Any): Can be a single Tool, a list of Tools, a callable, or other forms.

        Raises:
            TypeError: If the tools argument type is unsupported.
        """
        if not update and tool in self:
            raise ValueError(f"Function {tool.name} is already registered.")
        if isinstance(tool, Callable):
            tool = func_to_tool(tool)
            tool = (
                tool[0] if isinstance(tool, list) and len(tool) == 1 else tool
            )
        if not isinstance(tool, Tool):
            raise TypeError("Please register a Tool object.")
        self.registry[tool.name] = tool
        return True

    def update_tools(self, tools: list | Tool | Callable):
        if isinstance(tools, Tool) or isinstance(tools, Callable):
            return self._register_tool(tools, update=True)
        else:
            return all(lcall(tools, self._register_tool, update=True))

    def register_tools(self, tools: list | Tool | Callable):
        """
        Registers multiple Tools.

        Args:
            tools (list): The list of Tools to register.

        Returns:
            bool: True if all tools are successfully registered.
        """
        if isinstance(tools, Tool) or isinstance(tools, Callable):
            return self._register_tool(tools)
        else:
            return all(lcall(tools, self._register_tool))

    async def invoke(self, func_calling=None):
        """
        Invokes a function based on the provided function calling description.

        Args:
            func_calling (Any, optional): The function calling description, which can be:
                - tuple: (name, kwargs)
                - dict: {"function": name, "arguments": kwargs}
                - str: JSON string of dict format
                - ActionRequest object
                - FunctionCalling object

        Returns:
            Any: The result of the function call.

        Raises:
            ValueError: If func_calling is None or the function is not registered.
        """
        if not func_calling:
            raise ValueError("func_calling is required.")

        if not isinstance(func_calling, FunctionCalling):
            func_calling = FunctionCalling.create(func_calling)

        if func_calling.func_name in self.registry:
            return await self.registry[func_calling.func_name].invoke(
                func_calling=func_calling
            )

        raise ValueError(
            f"Function {func_calling.func_name} is not registered."
        )

    @property
    def _schema_list(self) -> list[dict[str, Any]]:
        """
        Lists all tool schemas currently registered in the ToolManager.

        Returns:
            list[dict[str, Any]]: A list of tool schemas.
        """
        return [tool.schema_ for tool in self.registry.values()]

    def get_tool_schema(self, tools: TOOL_TYPE, **kwargs) -> dict:
        """
        Retrieves the schema for a specific tool or all tools based on the input.

        Args:
            tools (TOOL_TYPE): Can be a boolean, specific tool name, Tool, or list of tools.
            **kwargs: Additional keyword arguments to be merged with tool schema.

        Returns:
            dict: Combined tool schema and kwargs.
        """
        if isinstance(tools, bool):
            tool_kwarg = {"tools": self._schema_list}
            return tool_kwarg | kwargs

        else:
            tool_kwarg = {"tools": self._get_tool_schema(tools)}
            return tool_kwarg | kwargs

    @singledispatchmethod
    def _get_tool_schema(self, tool: Any) -> dict:
        """
        Retrieves the schema for a specific tool based on its type.

        Args:
            tool (Any): The tool descriptor, can be a dict, Tool, str, or list.

        Raises:
            TypeError: If the tool type is unsupported.
        """
        raise TypeError(f"Unsupported type {type(tool)}")

    @_get_tool_schema.register(dict)
    def _(self, tool):
        """
        Assumes that the tool is a schema and returns it.

        Args:
            tool (dict): The tool schema.

        Returns:
            dict: The tool schema.
        """
        return tool

    @_get_tool_schema.register(Tool)
    def _(self, tool):
        """
        Retrieves the schema for a Tool object.

        Args:
            tool (Tool): The Tool object.

        Returns:
            dict: The tool schema.

        Raises:
            ValueError: If the Tool is not registered.
        """
        if tool.name in self.registry:
            return self.registry[tool.name].schema_
        else:
            err_msg = f"Function {tool.name} is not registered."
            raise ValueError(err_msg)

    @_get_tool_schema.register(str)
    def _(self, tool):
        """
        Assumes that the tool is a name and retrieves its schema.

        Args:
            tool (str): The tool name.

        Returns:
            dict: The tool schema.

        Raises:
            ValueError: If the tool name is not registered.
        """
        if tool in self.registry:
            return self.registry[tool].schema_
        else:
            err_msg = f"Function {tool} is not registered."
            raise ValueError(err_msg)

    @_get_tool_schema.register(list)
    def _(self, tools):
        """
        Retrieves the schema for a list of tools.

        Args:
            tools (list): The list of tools.

        Returns:
            list: A list of tool schemas.
        """
        return lcall(tools, self._get_tool_schema)

    def parse_tool(self, tools: TOOL_TYPE, **kwargs) -> dict:
        """
        Parses and merges tool schemas based on the provided tool descriptors.

        Args:
            tools (TOOL_TYPE): The tools to parse, can be a single tool or list.
            **kwargs: Additional keyword arguments to be merged with the tool schema.

        Returns:
            dict: The merged tool schema and additional arguments.
        """
        if tools:
            if isinstance(tools, bool):
                tool_kwarg = {"tools": self._schema_list}
                kwargs = tool_kwarg | kwargs
            else:
                tools = (
                    to_list(tools) if not isinstance(tools, list) else [tools]
                )
                tool_kwarg = {"tools": lcall(tools, self._get_tool_schema)}
                kwargs = tool_kwarg | kwargs

        return kwargs

    @staticmethod
    def parse_tool_request(response: dict) -> tuple[str, dict]:
        """
        Parses a tool request from a given response dictionary.

        Args:
            response (dict): The response data containing the tool request.

        Returns:
            Tuple[str, dict]: The function name and its arguments.

        Raises:
            ValueError: If the response is not a valid function call.
        """
        try:
            func = response["action"][7:]
            args = to_dict(response["arguments"])
            return func, args
        except Exception:
            try:
                func = response["recipient_name"].split(".")[-1]
                args = response["parameters"]
                return func, args
            except:
                raise ValueError("response is not a valid function call")


def func_to_tool(
    func_: Callable | list[Callable],
    parser: Callable | list[Callable] = None,
    docstring_style: str = "google",
    **kwargs,
) -> list[Tool]:
    """
    Converts functions to Tool objects, optionally associating parsers with each function
    and applying a specified docstring parsing style to generate tool schemas.

    Args:
        func_ (Callable | list[Callable]): The function(s) to convert into tool(s).
        parser (Callable | list[Callable], optional): Parser(s) to associate with
            the function(s). If a list is provided, it should match the length of func_.
        docstring_style (str, optional): The style of the docstring parser to use when
            generating tool schemas. Defaults to "google".

    Returns:
        list[Tool]: A list of Tool objects created from the provided function(s).

    Raises:
        ValueError: If the length of the parsers does not match the length of the
            functions when both are provided as lists.

    Examples:
        # Convert a single function with a custom parser
        tools = func_to_tool(my_function, my_parser)

        # Convert multiple functions without parsers
        tools = func_to_tool([func_one, func_two])

        # Convert multiple functions with multiple parsers
        tools = func_to_tool([func_one, func_two], [parser_one, parser_two])
    """
    fs = []
    funcs = to_list(func_, flatten=True, dropna=True)
    parsers = to_list(parser, flatten=True, dropna=True)

    if parser:
        if len(funcs) != len(parsers) != 1:
            raise ValueError(
                "Length of parser must match length of func. Except if you only pass one"
            )

        for idx in range(len(funcs)):
            f_ = lambda _f: Tool(
                function=_f,
                schema_=function_to_schema(_f, style=docstring_style),
                parser=parsers[idx] if len(parsers) > 1 else parsers[0],
                **kwargs,
            )

            fs.append(f_)

    else:
        fs = lcall(
            funcs,
            lambda _f: Tool(
                function=_f,
                schema_=function_to_schema(_f, style=docstring_style),
                **kwargs,
            ),
        )

    return fs
