import json
import asyncio
from typing import Dict, Union, List, Tuple, Any
from lionagi.utils import lcall
from lionagi.schema import BaseNode, Tool


class ToolManager(BaseNode):
    """
    A manager class to handle registration and invocation of tools that are subclasses of Tool.
    
    Attributes:
        registry (Dict[str, Tool]): A dictionary to hold registered tools, using their names as keys.
    """
    registry: Dict = {}

    def name_existed(self, name: str) -> bool:
        """
        Check if a tool name already exists in the registry.

        Parameters:
            name (str): The name of the tool to check.

        Returns:
            bool: True if the name exists, False otherwise.

        Examples:
            >>> tool_manager.name_existed('existing_tool')
            True
            >>> tool_manager.name_existed('nonexistent_tool')
            False
        """
        return True if name in self.registry.keys() else False
            
    def _register_tool(self, tool: Tool) -> None:
        """
        Register a new tool in the registry if it's an instance of Tool.

        Parameters:
            tool (Tool): The tool instance to register.

        Raises:
            TypeError: If the provided tool is not an instance of Tool.

        Examples:
            >>> tool_manager._register_tool(Tool())
            # Tool is registered without any output
        """
        if not isinstance(tool, Tool):
            raise TypeError('Please register a Tool object.')
        name = tool.schema_['function']['name']
        self.registry.update({name: tool})
                
    async def invoke(self, func_call: Tuple[str, Dict[str, Any]]) -> Any:
        """
        Invoke a registered tool's function with the provided arguments.

        Args:
            func_call (Tuple[str, Dict[str, Any]]): A tuple containing the tool's function name and kwargs.

        Returns:
            Any: The result of the tool's function invocation.

        Raises:
            ValueError: If the function is not registered or an error occurs during invocation.

        Examples:
            >>> await tool_manager.invoke(('registered_function', {'arg1': 'value1'}))
            # Result of the registered_function with given arguments
        """
        name, kwargs = func_call
        if self.name_existed(name):
            tool = self.registry[name]
            func = tool.func
            parser = tool.parser
            try:
                if asyncio.iscoroutinefunction(func):
                    return await parser(func(**kwargs)) if parser else func(**kwargs)
                else:
                    return parser(func(**kwargs)) if parser else func(**kwargs)
            except Exception as e:
                raise ValueError(f"Error when invoking function {name} with arguments {kwargs} with error message {e}")
        else: 
            raise ValueError(f"Function {name} is not registered.")
    
    @staticmethod
    def get_function_call(response: Dict) -> Tuple[str, Dict]:
        """
        Extract function name and arguments from a response JSON.

        Parameters:
            response (Dict): The JSON response containing function information.

        Returns:
            Tuple[str, Dict]: The function name and its arguments.

        Raises:
            ValueError: If the response is not a valid function call.

        Examples:
            >>> ToolManager.get_function_call({"action": "execute_add", "arguments": '{"x":1, "y":2}'})
            ('add', {'x': 1, 'y': 2})
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
        Register multiple tools using a given list.

        Parameters:
            tools (List[Tool]): A list of Tool instances to register.

        Examples:
            >>> tool_manager.register_tools([Tool(), Tool()])
            # Multiple Tool instances registered
        """
        lcall(tools, self._register_tool) #, update=update, new=new, prefix=prefix, postfix=postfix)

    def to_tool_schema_list(self) -> List[Dict[str, Any]]:
        """
        Convert the registry of tools to a list of their schemas.

        Returns:
            List[Dict[str, Any]]: A list of tool schemas.

        Examples:
            >>> tool_manager.to_tool_schema_list()
            # Returns a list of registered tool schemas
        """
        schema_list = []
        for tool in self.registry.values():
            schema_list.append(tool.schema_)
        return schema_list

    def _tool_parser(self, tools: Union[Dict, Tool, List[Tool], str, List[str], List[Dict]], **kwargs) -> Dict:
        """
        Parse tools and additional keyword arguments to form a dictionary used for tool configuration.

        Parameters:
            tools: A single tool object, a list of tool objects, a tool name, a list of tool names, or a dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict: A dictionary of tools and additional keyword arguments.

        Raises:
            ValueError: If a tool name string does not correspond to a registered tool.

        Examples:
            >>> tool_manager._tool_parser('registered_tool')
            # Returns a dictionary containing the schema of the registered tool
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
    