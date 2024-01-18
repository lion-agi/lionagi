import json
import asyncio
from typing import Dict
from lionagi.utils import lcall
from lionagi.schema import BaseNode, Tool


class ToolManager(BaseNode):
    registry: Dict = {}

    def name_existed(self, name: str):
        return True if name in self.registry.keys() else False
            
    def _register_tool(self, tool): #,update=False, new=False, prefix=None, postfix=None):
        
        # if self._name_existed(tool.name):
        #     if update and new:
        #         raise ValueError(f"Cannot both update and create new registry for existing function {tool.name} at the same time")

            # if len(name) > len(tool.func.__name__):
            #     if new and not postfix:
            #         try:
            #             idx = str_to_num(name[-3:], int)
            #             if idx > 0:
            #                 postfix = idx + 1
            #         except:
            #             pass

        # name = f"{prefix or ''}{name}{postfix}" if new else tool.func.__name__

        if not isinstance(tool, Tool):
            raise TypeError('Please register a Tool object.')
        name = tool.schema_['function']['name']
        self.registry.update({name: tool})
                
    async def invoke(self, func_call):
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
    def get_function_call(response):
        """
        Extract function name and arguments from a response JSON.

        Parameters:
            response (dict): The JSON response containing function information.

        Returns:
            Tuple[str, dict]: The function name and its arguments.
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
    
    def register_tools(self, tools): #, update=False, new=False, prefix=None, postfix=None ):
        lcall(tools, self._register_tool) #, update=update, new=new, prefix=prefix, postfix=postfix)

    def to_tool_schema_list(self):
        schema_list = []
        for tool in self.registry.values():
            schema_list.append(tool.schema_)
        return schema_list


# import asyncio
# import json
# from typing import Dict, Any, Optional, List, Tuple

# from lionagi.schema.base_tool import Tool
# from lionagi.utils.type_util import to_list
# from lionagi.utils.tool_util import func_to_tool

# class ToolRegistry:
#     """
#     ToolManager manages the registration and invocation of tools.

#     This class provides functionalities to register tools, check for their existence,
#     and invoke them dynamically with specified arguments.

#     Attributes:
#         registry (Dict[str, BaseTool]): A dictionary to store registered tools by name.
    
#     Methods:
#         _name_exists: Checks if a tool name already exists in the registry.
        
#         _register_tool: Registers a tool in the registry.
        
#         invoke: Dynamically invokes a registered tool with given arguments.
        
#         register_tools: Registers multiple tools in the registry.
#     """    
    
#     def __init__(self):
#         """
#         Initializes the ToolManager with an empty registry.
#         """        
#         self.registry: Dict[str, Tool] = {}

#     def _name_exists(self, name: str) -> bool:
#         """
#         Checks if a tool name already exists in the registry.

#         Parameters:
#             name (str): The name of the tool to check.

#         Returns:
#             bool: True if the name exists in the registry, False otherwise.
#         """
#         return name in self.registry

#     def _register_tool(self, tool: Tool, name: Optional[str] = None, update: bool = False, new: bool = False, prefix: Optional[str] = None, postfix: Optional[int] = None):
#         """
#         Registers a tool in the registry.

#         Parameters:
#             tool (BaseTool): The tool to be registered.
            
#             name (Optional[str]): The name to register the tool with. Defaults to the tool's function name.
            
#             update (bool): If True, updates the existing tool. Defaults to False.
            
#             new (bool): If True, creates a new registry entry. Defaults to False.
            
#             prefix (Optional[str]): A prefix for the tool name.
            
#             postfix (Optional[int]): A postfix for the tool name.

#         Raises:
#             ValueError: If both update and new are True for an existing function.
#         """
#         name = name or tool.func.__name__
#         original_name = name

#         if self._name_exists(name):
#             if update and new:
#                 raise ValueError("Cannot both update and create new registry for existing function.")
#             if new:
#                 idx = 1
#                 while self._name_exists(f"{prefix or ''}{name}{postfix or ''}{idx}"):
#                     idx += 1
#                 name = f"{prefix or ''}{name}{postfix or ''}{idx}"
#             else:
#                 self.registry.pop(original_name, None)

#         self.registry[name] = tool

#     async def invoke(self, name_kwargs: Tuple) -> Any:
#         """
#         Dynamically invokes a registered tool with given arguments.

#         Parameters:
#             name (str): The name of the tool to invoke.
            
#             kwargs (Dict[str, Any]): A dictionary of keyword arguments to pass to the tool.

#         Returns:
#             Any: The result of the tool invocation.

#         Raises:
#             ValueError: If the tool is not registered or if an error occurs during invocation.
#         """
#         name, kwargs = name_kwargs
#         if not self._name_exists(name):
#             raise ValueError(f"Function {name} is not registered.")

#         tool = self.registry[name]
#         func = tool.func
#         parser = tool.parser

#         try:
#             result = await func(**kwargs) if asyncio.iscoroutinefunction(func) else func(**kwargs)
#             return await parser(result) if parser and asyncio.iscoroutinefunction(parser) else parser(result) if parser else result
#         except Exception as e:
#             raise ValueError(f"Error invoking function {name}: {str(e)}")

#     def register_tools(self, tools: List[Tool], update: bool = False, new: bool = False,
#                        prefix: Optional[str] = None, postfix: Optional[int] = None):
#         """
#         Registers multiple tools in the registry.

#         Parameters:
#             tools (List[BaseTool]): A list of tools to register.
            
#             update (bool): If True, updates existing tools. Defaults to False.
            
#             new (bool): If True, creates new registry entries. Defaults to False.
            
#             prefix (Optional[str]): A prefix for the tool names.
            
#             postfix (Optional[int]): A postfix for the tool names.
#         """        
#         for tool in tools:
#             self._register_tool(tool, update=update, new=new, prefix=prefix, postfix=postfix)

#     def _register_func(self, func_, parser=None, **kwargs):
#         # kwargs for _register_tool
        
#         tool = func_to_tool(func_=func_, parser=parser)
#         self._register_tool(tool=tool, **kwargs)
    
#     def register_funcs(self, funcs, parsers=None, **kwargs):
#         funcs, parsers = to_list(funcs), to_list(parsers)
#         if parsers is not None and len(parsers) != len(funcs):
#             raise ValueError("The number of funcs and tools should be the same")
#         parsers = parsers or [None for _ in range(len(funcs))]
        
#         for i, func in enumerate(funcs):
#             self._register_func(func_=func, parser=parsers[i], **kwargs)
            
#     @staticmethod
#     def get_function_call(response):
#         """
#         Extract function name and arguments from a response JSON.

#         Parameters:
#             response (dict): The JSON response containing function information.

#         Returns:
#             Tuple[str, dict]: The function name and its arguments.
#         """
#         try: 
#             # out = json.loads(response)
#             func = response['function'][5:]
#             args = json.loads(response['arguments'])
#             return (func, args)
#         except:
#             try:
#                 func = response['recipient_name'].split('.')[-1]
#                 args = response['parameters']
#                 return (func, args)
#             except:
#                 raise ValueError('response is not a valid function call')
            