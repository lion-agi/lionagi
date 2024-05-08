from functools import singledispatchmethod
from typing import Any, Callable
from lionagi.libs import ParseUtil
from lionagi.libs.ln_convert import to_list
from lionagi.libs.ln_func_call import lcall
from lionagi.core.generic.abc import Actionable
from .function_calling import FunctionCalling
from .tool import Tool, TOOL_TYPE


class ToolManager(Actionable):

    def __init__(self, registry: dict[str, Tool] = None) -> None:
        self.registry = registry or {}

    @singledispatchmethod
    def register_tools(self, tools: Any):
        raise TypeError(f"Unsupported type {type(tools)}")

    @register_tools.register(Tool)
    def _(self, tools):
        if tools.name in self.registry:
            raise ValueError(f"Function {tools.name} is already registered.")
        else:
            self.registry[tools.name] = tools
            return True

    @register_tools.register(Callable)
    def _(self, tools):
        tool = func_to_tool(tools)[0]
        return self.register_tools(tool)

    @register_tools.register(list)
    def _(self, tools):
        return all(lcall(tools, self.register_tools))

    async def invoke(self, func_calling=None):
        """
        func_calling can be
        - tuple: (name, kwargs)
        - dict: {"function": name, "arguments": kwargs}
        - str: json string of dict_ format
        - ActionRequest object
        - FunctionCalling object
        """
        if not func_calling:
            raise ValueError("func_calling is required.")

        if not isinstance(func_calling, FunctionCalling):
            func_calling = FunctionCalling.create(func_calling)

        if func_calling.func_name in self.registry:
            return await self.registry[func_calling.func_name].invoke(
                func_calling=func_calling
            )

        raise ValueError(f"Function {func_calling.func_name} is not registered.")

    @property
    def _schema_list(self) -> list[dict[str, Any]]:
        return [tool.schema_ for tool in self.registry.values()]

    def get_tool_schema(self, tools: TOOL_TYPE, **kwargs):
        if isinstance(tools, bool):
            tool_kwarg = {"tools": self._schema_list}
            return tool_kwarg | kwargs

        else:
            tool_kwarg = {"tools": self._get_tool_schema(tools)}
            return tool_kwarg | kwargs

    @singledispatchmethod
    def _get_tool_schema(self, tool: Any) -> dict:
        raise TypeError(f"Unsupported type {type(tool)}")

    @_get_tool_schema.register(dict)
    def _(self, tool):
        """assuming that the tool is a schema"""
        return tool

    @_get_tool_schema.register(Tool)
    def _(self, tool):
        if tool.name in self.registry:
            return self.registry[tool.name].schema_
        else:
            err_msg = f"Function {tool.name} is not registered."
            raise ValueError(err_msg)

    @_get_tool_schema.register(str)
    def _(self, tool):
        """assuming that the tool is a name"""
        if tool in self.registry:
            return self.registry[tool].schema_
        else:
            err_msg = f"Function {tool} is not registered."
            raise ValueError(err_msg)

    @_get_tool_schema.register(list)
    def _(self, tools):
        return lcall(tools, self._get_tool_schema)


def func_to_tool(
    func_: Callable | list[Callable], parser=None, docstring_style="google"
):

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
                func=_f,
                schema_=ParseUtil._func_to_schema(_f, style=docstring_style),
                parser=parsers[idx] if len(parsers) > 1 else parsers[0],
            )

            fs.append(f_)

    else:
        fs = lcall(
            funcs,
            lambda _f: Tool(
                func=_f, schema_=ParseUtil._func_to_schema(_f, style=docstring_style)
            ),
        )

    return fs
