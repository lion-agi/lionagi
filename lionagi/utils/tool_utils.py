import json
import asyncio
from typing import Callable, Any, Dict, Union, Optional
from .sys_utils import l_call, str_to_num
from ..schema import BaseNode, SimpleTool




class ToolManager(BaseNode):
    registry : Dict = {}
        
    def to_dict(name, tool):
        return {f"{name}": tool}

    def _name_existed(self, name):
        return True if name in self.registry.keys() else False
            
    def _register_function(self, name, tool, parser=None, content=None, update=False, new=False, prefix=None, postfix=None):
        if self._name_existed(name):
            if update and new:
                raise ValueError(f"Cannot both update and create new registry for existing function {name} at the same time")
            
            
        if len(name) > len(tool.func.__name__):
            if new and not postfix: 
                if str_to_num(name, int) is not None:
            
        
        
        name = f"{prefix or ''}{name}{postfix or i}" if new else name                
        self.registry.update(self._to_dict(name, func, content, parser)) 
                
    async def invoke(self, name, *args, **kwargs):
        if self._name_existed(name):
            func = self.registry[name]["function"]
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                raise ValueError(f"Error when invoking function {name} with arguments {*args, kwargs} with error message {e}")
        else: 
            raise ValueError(f"Function {name} is not registered.")
    
    @staticmethod
    def _get_function_call(response):
        """
        Extract function name and arguments from a response JSON.

        Parameters:
            response (str): The JSON response containing function information.

        Returns:
            Tuple[str, dict]: The function name and its arguments.
        """
        try: 
            out = json.loads(response)
            func = out['function'][5:]
            args = json.loads(out['arguments'])
            return (func, args)
        except:
            try:
                out = json.loads(response)
                out = out['tool_uses'][0]
                func = out['recipient_name'].split('.')[-1]
                args = out['parameters']
                return (func, args)
            except:
                raise ValueError('response is not a valid function call')
    
    @staticmethod
    def _from_tool(tool, func):
        """
        Convert tool information to function registration parameters.

        Parameters:
            tool (dict): The tool information.
            func (callable): The function associated with the tool.

        Returns:
            Tuple[str, callable, list]: The function name, the function, and the list of function parameters.

        """
        return (tool['function']['name'], func, 
                tool['function']['parameters']['properties'].keys())
        
    def register_tools(self, tools, funcs, update=False, new=False, prefix=None, postfix=None):
        """
        Register multiple tools and their corresponding functions.

        Parameters:
            tools (list): The list of tool information dictionaries.
            functions (list): The list of corresponding functions.
            update (bool): Whether to update existing functions.
            new (bool): Whether to create new registries for existing functions.
            prefix (Optional[str]): A prefix to add to the function names.
            postfix (Optional[str]): A postfix to add to the function names.

        """
        _f = l_call(range(len(tools)), lambda i: self._from_tool(tools[i], funcs[i]))
        l_call(range(len(tools)), lambda i: self._register_function(_f[i][0], _f[i][1], update=update, new=new, prefix=prefix, postfix=postfix))
        