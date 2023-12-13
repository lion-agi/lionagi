import json
import asyncio
from .sys_util import l_call
    

class ToolManager:
    def __init__(self):
        self.registry = {}
        
    @staticmethod
    def _to_dict(name, function, content=None):
        return {name: {"function": function, "content": content or "none"}}

    def _name_existed(self, name):
        return True if name in self.registry.keys() else False
            
    def _register_function(self, name, function, content=None, update=False, new=False, prefix=None, postfix=None):
        if self._name_existed(name):
            if update and new:
                raise ValueError(f"Cannot both update and create new registry for existing function {name} at the same time")
            
        name = f"{prefix or ''}{name}{postfix or '1'}" if new else name                
        self.registry.update(self._to_dict(name, function, content)) 
                
    def invoke(self, name, args):
        if self._name_existed(name):
            try:
                return self.registry[name](**args)
            except Exception as e:
                raise ValueError(f"Error when invoking function {name} with arguments {args} with error message {e}")
        else: 
            raise ValueError(f"Function {name} is not registered.")
    
    async def ainvoke(self, name, args):
        if self._name_existed(name):
            function = self.registry[name]["function"]
            try:
                if asyncio.iscoroutinefunction(function):
                    return await function(**args)
                else:
                    return function(**args)
            except Exception as e:
                raise ValueError(f"Error when invoking function {name} with arguments {args} with error message {e}")
        else: 
            raise ValueError(f"Function {name} is not registered.")
    
    @staticmethod
    def _get_function_call(response):
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
        return (tool['function']['name'], func, 
                tool['function']['parameters']['properties'].keys())
        
    def register_tools(self, tools, functions, update=False, new=False, prefix=None, postfix=None):
        funcs = l_call(range(len(tools)), lambda i: self._from_tool(tools[i], functions[i]))
        l_call(range(len(tools)), lambda i: self._register_function(funcs[i][0], funcs[i][1], update=update, new=new, prefix=prefix, postfix=postfix))