from typing import Tuple, Any, Callable

from lionagi.libs import convert, func_call
from lionagi.new.schema.todo.tool import Tool, FunctionCalling

from ....to_do.working.old_core.action.func_to_tool import func_to_tool

class ToolManager:

    def __init__(self) -> None:
        self.registry = {}

    async def invoke(self, function_call: FunctionCalling):
        try:
            tool: Tool = self.get_tool(function_call.func_name)
            return await tool.invoke(function_call.kwargs)

        except Exception as e:
            raise ValueError(
                f"Error when invoking function {function_call[0]} with arguments {function_call[1]} with error message {e}"
            ) from e

    @staticmethod
    def get_oai_function_call(response: dict) -> Tuple[str, dict]:
        try:
            func = response["action"][7:]
            args = convert.to_dict(response["arguments"])
            return FunctionCalling.create((func, args))
        except Exception:
            try:
                func = response["recipient_name"].split(".")[-1]
                args = response["parameters"]
                return FunctionCalling.create((func, args))
            except:
                raise ValueError("response is not a valid function call")

    def parse_tool(self, tools: dict | Tool | str | bool | list, **kwargs) -> dict:

        if isinstance(tools, list):
            tools = [tools]

        kwargs = kwargs or {}
        return self.get_tool_schema(tools, kwargs)


    # Properties
    @property
    def tools(self):
        return list(self.registry.values())

    @property
    def tool_ids(self):
        return [tool.id_ for tool in self.tools]

    @property
    def tool_schema(self):
        return [tool.schema_ for tool in self.tools]

    @func_call.singledispatchmethod
    def has_tool(self, tool: Any):
        raise TypeError(f"objects of {type(tool)} cannot be checked for existence")

    @has_tool.register
    def _(self, tool: Tool):
        if tool.name in self.registry and self.registry[tool.name] == tool:
            return True
        return False

    @has_tool.register
    def _(self, tool: str):
        """either tool id or tool name"""
        if tool in self.registry or tool in self.tool_ids:
            return True
        return False

    ## get_tool, can take a tool name, tool instance, or tool id
    @func_call.singledispatchmethod
    def get_tool(self, tool: Any):
        raise TypeError(f"objects of {type(tool)} cannot be retrieved")

    @get_tool.register
    def _(self, tool: str):
        if tool in self.registry:
            return self.registry[tool]
        elif tool in self.tool_ids:
            return self.tools[self.tool_ids.index(tool)]
        raise ValueError(f"tool {tool} not found")

    @get_tool.register
    def _(self, tool: Tool):
        if self.has_tool(tool):
            return tool
        raise ValueError(f"tool {tool} not found")

    ## register_tool, take a tool/function, or a list/dict of [tools, functions]
    @func_call.singledispatchmethod
    def register_tool(self, tools: Any):
        raise NotImplementedError(f"objects of {type(tools)} cannot be registered")

    @register_tool.register
    def _(self, tools: Tool) -> bool:
        name = tools.schema_["function"]["name"]
        self.registry.update({name: tools})
        return True

    @register_tool.register
    def _(self, tools: Callable) -> bool:
        tools = func_to_tool(tools)[0]
        return self.register_tool(tools)

    @register_tool.register
    def _(self, tools: list) -> bool:
        return all([self.register_tool(i) for i in tools])

    @register_tool.register
    def _(self, tools: dict) -> bool:
        return self.register_tool(list(tools.values()))

    ## deregister_tool
    @func_call.singledispatchmethod
    def deregister_tool(self, tool: Any):
        raise NotImplementedError(f"objects of {type(tool)} cannot be deregistered")

    @deregister_tool.register
    def _(self, tool: str):
        if tool in self.registry:
            self.register_tool.pop(tool)
            return True
        return False

    @deregister_tool.register
    def _(self, tool: Tool):
        if self.has_tool(tool):
            return self.deregister_tool(tool.name)
        return False

    @deregister_tool.register
    def _(self, tool: list):
        return all([self.deregister_tool(i) for i in tool])

    @deregister_tool.register
    def _(self, tool: dict):
        return self.deregister_tool(list(tool.values()))

    @func_call.singledispatchmethod
    def get_tool_schema(self, tool: Any, kwargs: Any = {}):
        raise NotImplementedError(f"objects of {type(tool)} cannot be parsed")

    @get_tool_schema.register
    def _(self, tool: dict, kwargs: Any = {}):
        """assuming it's valid tool schema"""
        return tool

    @get_tool_schema.register
    def _(self, tool: Tool, kwargs: Any = {}):
        return tool.schema_

    @get_tool_schema.register
    def _(self, tool: str, kwargs: Any = {}):
        return self.get_tool_schema(self.get_tool(tool, kwargs=kwargs))

    @get_tool_schema.register
    def _(self, tool: bool, kwargs: Any = {}):
        tool_kwarg = {"tools": self.to_tool_schema_list()}
        return tool_kwarg | kwargs

    @get_tool_schema.register
    def _(self, tool: list, kwargs: Any = {}):
        tool_kwarg = {"tools": func_call.lcall(tool, self.get_tool_schema)}
        return tool_kwarg | kwargs
