# To-do

import json
import asyncio
import re
from typing import Dict, Union, List, Tuple, Any, Callable
from lionagi.util.call_util import lcall, is_coroutine_func, _call_handler, alcall
from lionagi.schema.base_node import BaseNode, Tool


class ActionManager:

    registry: Dict = {}

    def name_existed(self, name: str) -> bool:

        return True if name in self.registry.keys() else False
            
    def _register_tool(self, tool: Tool) -> None:
        if not isinstance(tool, Tool):
            raise TypeError('Please register a Tool object.')
        name = tool.schema_['function']['name']
        self.registry.update({name: tool})
                
    async def invoke(self, func_call: Tuple[str, Dict[str, Any]]) -> Any:
        name, kwargs = func_call
        if self.name_existed(name):
            tool = self.registry[name]
            func = tool.func
            parser = tool.parser
            try:
                if is_coroutine_func(func):
                    tasks = [_call_handler(func, **kwargs)]
                    out = await asyncio.gather(*tasks)
                    return parser(out[0]) if parser else out[0]
                else:
                    out = func(**kwargs)
                    return parser(out) if parser else out
            except Exception as e:
                raise ValueError(f"Error when invoking function {name} with arguments {kwargs} with error message {e}")
        else: 
            raise ValueError(f"Function {name} is not registered.")
    
    @staticmethod
    def get_function_call(response: Dict) -> Tuple[str, Dict]:
        try:
            func = response['action'][7:]
            args = json.loads(response['arguments'])
            return (func, args)
        except:
            try:
                func = response['recipient_name'].split('.')[-1]
                args = response['parameters']
                return (func, args)
            except:
                raise ValueError('response is not a valid function call')
    
    def register_tools(self, tools: List[Tool]) -> None:
        lcall(tools, self._register_tool) 

    def to_tool_schema_list(self) -> List[Dict[str, Any]]:
        schema_list = []
        for tool in self.registry.values():
            schema_list.append(tool.schema_)
        return schema_list

    def _tool_parser(self, tools: Union[Dict, Tool, List[Tool], str, List[str], List[Dict]], **kwargs) -> Dict:
        def tool_check(tool):
            if isinstance(tool, dict):
                return tool
            elif isinstance(tool, Tool):
                return tool.schema_
            elif isinstance(tool, str):
                if self.name_existed(tool):
                    tool = self.registry[tool]
                    return tool.schema_
                else:
                    raise ValueError(f'Function {tool} is not registered.')

        if isinstance(tools, bool):
            tool_kwarg = {"tools": self.to_tool_schema_list()}
            kwargs = {**tool_kwarg, **kwargs}

        else:
            if not isinstance(tools, list):
                tools = [tools]
            tool_kwarg = {"tools": lcall(tools, tool_check)}
            kwargs = {**tool_kwarg, **kwargs}
            
        return kwargs

    # def register_tool_with_grammar(self, tool: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
    #     """Registers a tool with associated grammar for advanced parsing."""
    #     if not isinstance(tool, Tool):
    #         raise TypeError("Please register a Tool object.")
    #     name = tool.schema_['function']['name']
    #     self.registry[name] = {"tool": tool, "grammar": grammar}
    #
    # async def invoke_with_grammar(self, func_call: str) -> Any:
    #     """Invokes a registered tool using a grammar-based approach for parsing the function call."""
    #     for name, data in self.registry.items():
    #         tool = data["tool"]
    #         grammar = data["grammar"]
    #         match = grammar(func_call)
    #         if match:
    #             args, kwargs = match
    #             func = tool.func
    #             try:
    #                 if is_coroutine_func(func):
    #                     return await func(*args, **kwargs)
    #                 else:
    #                     return func(*args, **kwargs)
    #             except Exception as e:
    #                 raise ValueError(f"Error when invoking function {name}: {e}")
    #     raise ValueError("No registered tool matches the function call.")
    #
    # def register_tool_with_grammar(self, tool: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
    #     if not isinstance(tool, Tool):
    #         raise TypeError("Expected a Tool object for registration.")
    #     name = tool.schema_['function']['name']
    #     # Ensures each tool is associated with its unique grammar for parsing calls
    #     self.registry[name] = {"tool": tool, "grammar": grammar}
    #
    # async def invoke_with_grammar(self, func_call: str) -> Any:
    #     for name, data in self.registry.items():
    #         if "grammar" in data:  # Ensure only tools with grammar are processed
    #             tool, grammar = data["tool"], data["grammar"]
    #             match = grammar(func_call)
    #             if match:
    #                 args, kwargs = match
    #                 func = tool.func
    #                 try:
    #                     # Checks if the function is asynchronous and calls it appropriately
    #                     if asyncio.iscoroutinefunction(func):
    #                         return await func(*args, **kwargs)
    #                     else:
    #                         return func(*args, **kwargs)
    #                 except Exception as e:
    #                     raise ValueError(f"Error invoking {name} with {args}, {kwargs}: {e}")
    #     raise ValueError(f"No registered tool matches the function call: {func_call}")
    #
