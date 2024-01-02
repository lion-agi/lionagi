import asyncio
from typing import Dict, Any, Optional, List

from lionagi.schema.base_tool import Tool
from lionagi.utils.type_util import to_list
from lionagi.utils.tool_util import func_to_tool

class ToolRegistry:
    """
    ToolManager manages the registration and invocation of tools.

    This class provides functionalities to register tools, check for their existence,
    and invoke them dynamically with specified arguments.

    Attributes:
        registry (Dict[str, BaseTool]): A dictionary to store registered tools by name.
    
    Methods:
        _name_exists: Checks if a tool name already exists in the registry.
        
        _register_tool: Registers a tool in the registry.
        
        invoke: Dynamically invokes a registered tool with given arguments.
        
        register_tools: Registers multiple tools in the registry.
    """    
    
    def __init__(self):
        """
        Initializes the ToolManager with an empty registry.
        """        
        self.registry: Dict[str, Tool] = {}

    def _name_exists(self, name: str) -> bool:
        """
        Checks if a tool name already exists in the registry.

        Parameters:
            name (str): The name of the tool to check.

        Returns:
            bool: True if the name exists in the registry, False otherwise.
        """
        return name in self.registry

    def _register_tool(self, tool: Tool, name: Optional[str] = None, update: bool = False, new: bool = False, prefix: Optional[str] = None, postfix: Optional[int] = None):
        """
        Registers a tool in the registry.

        Parameters:
            tool (BaseTool): The tool to be registered.
            
            name (Optional[str]): The name to register the tool with. Defaults to the tool's function name.
            
            update (bool): If True, updates the existing tool. Defaults to False.
            
            new (bool): If True, creates a new registry entry. Defaults to False.
            
            prefix (Optional[str]): A prefix for the tool name.
            
            postfix (Optional[int]): A postfix for the tool name.

        Raises:
            ValueError: If both update and new are True for an existing function.
        """
        name = name or tool.func.__name__
        original_name = name

        if self._name_exists(name):
            if update and new:
                raise ValueError("Cannot both update and create new registry for existing function.")
            if new:
                idx = 1
                while self._name_exists(f"{prefix or ''}{name}{postfix or ''}{idx}"):
                    idx += 1
                name = f"{prefix or ''}{name}{postfix or ''}{idx}"
            else:
                self.registry.pop(original_name, None)

        self.registry[name] = tool

    async def invoke(self, name: str, kwargs: Dict) -> Any:
        """
        Dynamically invokes a registered tool with given arguments.

        Parameters:
            name (str): The name of the tool to invoke.
            
            kwargs (Dict[str, Any]): A dictionary of keyword arguments to pass to the tool.

        Returns:
            Any: The result of the tool invocation.

        Raises:
            ValueError: If the tool is not registered or if an error occurs during invocation.
        """        
        if not self._name_exists(name):
            raise ValueError(f"Function {name} is not registered.")

        tool = self.registry[name]
        func = tool.func
        parser = tool.parser

        try:
            result = await func(**kwargs) if asyncio.iscoroutinefunction(func) else func(**kwargs)
            return await parser(result) if parser and asyncio.iscoroutinefunction(parser) else parser(result) if parser else result
        except Exception as e:
            raise ValueError(f"Error invoking function {name}: {str(e)}")

    def register_tools(self, tools: List[Tool], update: bool = False, new: bool = False,
                       prefix: Optional[str] = None, postfix: Optional[int] = None):
        """
        Registers multiple tools in the registry.

        Parameters:
            tools (List[BaseTool]): A list of tools to register.
            
            update (bool): If True, updates existing tools. Defaults to False.
            
            new (bool): If True, creates new registry entries. Defaults to False.
            
            prefix (Optional[str]): A prefix for the tool names.
            
            postfix (Optional[int]): A postfix for the tool names.
        """        
        for tool in tools:
            self._register_tool(tool, update=update, new=new, prefix=prefix, postfix=postfix)

    def _register_func(self, func_, parser=None, **kwargs):
        # kwargs for _register_tool
        
        tool = func_to_tool(func_=func_, parser=parser)
        self._register_tool(tool=tool, **kwargs)
    
    def register_funcs(self, funcs, parsers=None, **kwargs):
        funcs, parsers = to_list(funcs), to_list(parsers)
        if parsers is not None and len(parsers) != len(funcs):
            raise ValueError("The number of funcs and tools should be the same")
        parsers = parsers or [None for _ in range(len(funcs))]
        
        for i, func in enumerate(funcs):
            self._register_func(func_=func, parser=parsers[i], **kwargs)