import json
import asyncio
from typing import Dict
from ..utils.sys_utils import l_call, str_to_num
from ..schema import BaseNode


class ToolManager(BaseNode):
    registry : Dict = {}

    def _name_existed(self, name: str):
        return True if name in self.registry.keys() else False
            
    def _register_tool(self, tool, name: str=None, update=False, new=False, prefix=None, postfix=None):
        
        if self._name_existed(name):
            if update and new:
                raise ValueError(f"Cannot both update and create new registry for existing function {name} at the same time")

            if len(name) > len(tool.func.__name__):
                if new and not postfix: 
                    try:
                        idx = str_to_num(name[-3:], int)
                        if idx > 0: 
                            postfix = idx + 1
                    except:
                        pass

        name = f"{prefix or ''}{name}{postfix}" if new else tool.func.__name__                
        self.registry.update({name:tool}) 
                
    async def invoke(self, name, kwargs):
        if self._name_existed(name):
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
    
    def register_tools(self, tools, update=False, new=False, prefix=None, postfix=None ):
        l_call(tools, self._register_tool, update=update, new=new, prefix=prefix, postfix=postfix)
        