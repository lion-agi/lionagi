import json
import asyncio
from typing import Dict, Union, List, Tuple, Any
from lionagi.utils.call_util import lcall, is_coroutine_func, _call_handler, alcall
from lionagi.schema import BaseNode, Tool


class ToolManager(BaseNode):
    """
    A manager class for handling the registration and invocation of tools that are subclasses of Tool.
    
    This class maintains a registry of tool instances, allowing for dynamic invocation based on
    tool name and provided arguments. It supports both synchronous and asynchronous tool function
    calls.

    Attributes:
        registry (Dict[str, Tool]): A dictionary to hold registered tools, keyed by their names.
    """
    registry: Dict = {}

    def name_existed(self, name: str) -> bool:
        """
        Checks if a tool name already exists in the registry.

        Args:
            name (str): The name of the tool to check.

        Returns:
            bool: True if the name exists, False otherwise.
        """
        return True if name in self.registry.keys() else False
            
    def _register_tool(self, tool: Tool) -> None:
        """
        Registers a tool in the registry. Raises a TypeError if the object is not an instance of Tool.

        Args:
            tool (Tool): The tool instance to register.

        Raises:
            TypeError: If the provided object is not an instance of Tool.
        """
        if not isinstance(tool, Tool):
            raise TypeError('Please register a Tool object.')
        name = tool.schema_['function']['name']
        self.registry.update({name: tool})
                
    async def invoke(self, func_call: Tuple[str, Dict[str, Any]]) -> Any:
        """
        Invokes a registered tool's function with the given arguments. Supports both coroutine and regular functions.

        Args:
            func_call (Tuple[str, Dict[str, Any]]): A tuple containing the function name and a dictionary of keyword arguments.

        Returns:
            Any: The result of the function call.

        Raises:
            ValueError: If the function name is not registered or if there's an error during function invocation.
        """
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
        """
        Extracts a function call and arguments from a response dictionary.

        Args:
            response (Dict): The response dictionary containing the function call information.

        Returns:
            Tuple[str, Dict]: A tuple containing the function name and a dictionary of arguments.

        Raises:
            ValueError: If the response does not contain valid function call information.
        """
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
        """
        Registers multiple tools in the registry.

        Args:
            tools (List[Tool]): A list of tool instances to register.
        """
        lcall(tools, self._register_tool) 

    def to_tool_schema_list(self) -> List[Dict[str, Any]]:
        """
        Generates a list of schemas for all registered tools.

        Returns:
            List[Dict[str, Any]]: A list of tool schemas.
        
        """
        schema_list = []
        for tool in self.registry.values():
            schema_list.append(tool.schema_)
        return schema_list

    def _tool_parser(self, tools: Union[Dict, Tool, List[Tool], str, List[str], List[Dict]], **kwargs) -> Dict:
        """
        Parses tool information and generates a dictionary for tool invocation.

        Args:
            tools: Tool information which can be a single Tool instance, a list of Tool instances, a tool name, or a list of tool names.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict: A dictionary containing tool schema information and any additional keyword arguments.

        Raises:
            ValueError: If a tool name is provided that is not registered.
        """
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
