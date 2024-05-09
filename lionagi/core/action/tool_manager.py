from functools import singledispatchmethod
from typing import Any, Callable, Tuple
from lionagi.libs import ParseUtil
from lionagi.libs.ln_convert import to_list, to_dict
from lionagi.libs.ln_func_call import lcall
from lionagi.core.generic.abc import Actionable
from lionagi.core.action.function_calling import FunctionCalling
from lionagi.core.action.tool import Tool, TOOL_TYPE


class ToolManager(Actionable):

    def __init__(self, registry: dict[str, Tool] = None) -> None:
        self.registry = registry or {}

    @singledispatchmethod
    def register_tools(self, tools: Any):
        if isinstance(tools, Callable):
            tool = func_to_tool(tools)[0]
            return self.register_tools(tool)
        
        raise TypeError(f"Unsupported type {type(tools)}")

    @register_tools.register
    def _(self, tools: Tool):
        if tools.name in self.registry:
            raise ValueError(f"Function {tools.name} is already registered.")
        else:
            self.registry[tools.name] = tools
            return True

    @register_tools.register
    def _(self, tools: list):
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

    def parse_tool(self, tools: TOOL_TYPE, **kwargs) -> dict:

        def tool_check(tool):
            if isinstance(tool, dict):
                return tool
            elif isinstance(tool, Tool):
                return tool.schema_
            elif isinstance(tool, str):
                if tool in self.registry:
                    tool: Tool = self.registry[tool]
                    return tool.schema_
                else:
                    raise ValueError(f"Function {tool} is not registered.")

        if tools:
            if isinstance(tools, bool):
                tool_kwarg = {"tools": self._schema_list}
                kwargs = tool_kwarg | kwargs

            else:
                if not isinstance(tools, list):
                    tools = [tools]
                tool_kwarg = {"tools": lcall(tools, tool_check)}
                kwargs = tool_kwarg | kwargs

        return kwargs

    @staticmethod
    def parse_tool_response(response: dict) -> Tuple[str, dict]:
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
