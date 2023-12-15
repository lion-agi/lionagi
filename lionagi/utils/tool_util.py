import json
import asyncio
from .sys_util import l_call
    

class ToolManager:
    """
    A manager class for handling and invoking registered tools and functions.

    This class allows the registration of tools and functions, enabling their invocation.

    Attributes:
        registry (dict): A dictionary storing the registered tools and their corresponding functions.

    Methods:
        _to_dict(name, function, content=None) -> dict:
            Convert tool information to a dictionary entry.

        _name_existed(name) -> bool:
            Check if a given name exists in the registry.

        _register_function(name, function, content=None, update=False, new=False, prefix=None, postfix=None) -> None:
            Register a function with a specified name in the registry.

        invoke(name, args) -> Any:
            Invoke a registered function with the provided arguments.

        ainvoke(name, args) -> Any:
            Asynchronously invoke a registered function with the provided arguments.

        _get_function_call(response) -> Tuple[str, dict]:
            Extract function name and arguments from a response JSON.

        _from_tool(tool, func) -> Tuple[str, callable, list]:
            Convert tool information to function registration parameters.

        register_tools(tools, functions, update=False, new=False, prefix=None, postfix=None) -> None:
            Register multiple tools and their corresponding functions.
    """
    def __init__(self):
        """
        Initialize a ToolManager object with an empty registry.
        """
        self.registry = {}
        
    @staticmethod
    def _to_dict(name, function, content=None):
        """
        Convert tool information to a dictionary entry.

        Parameters:
            name (str): The name of the tool.
            function (callable): The function associated with the tool.
            content (Optional[str]): Additional content for the tool.

        Returns:
            dict: A dictionary entry representing the tool.
        """
        return {name: {"function": function, "content": content or "none"}}

    def _name_existed(self, name):
        """
        Check if a given name exists in the registry.

        Parameters:
            name (str): The name to check.

        Returns:
            bool: True if the name exists in the registry, False otherwise.

        """
        return True if name in self.registry.keys() else False
            
    def _register_function(self, name, function, content=None, update=False, new=False, prefix=None, postfix=None):
        """
        Register a function with a specified name in the registry.

        Parameters:
            name (str): The name of the function.
            function (callable): The function to register.
            content (Optional[str]): Additional content for the function.
            update (bool): Whether to update an existing function with the same name.
            new (bool): Whether to create a new registry for an existing function.
            prefix (Optional[str]): A prefix to add to the function name.
            postfix (Optional[str]): A postfix to add to the function name.

        """
        if self._name_existed(name):
            if update and new:
                raise ValueError(f"Cannot both update and create new registry for existing function {name} at the same time")
            
        name = f"{prefix or ''}{name}{postfix or '1'}" if new else name                
        self.registry.update(self._to_dict(name, function, content)) 
                
    def invoke(self, name, kwargs):
        """
        Invoke a registered function with the provided arguments.

        Parameters:
            name (str): The name of the function to invoke.
            kwargs (dict): The arguments to pass to the function.

        Returns:
            Any: The result of invoking the function.
        """
        if self._name_existed(name):
            try:
                return self.registry[name](**kwargs)
            except Exception as e:
                raise ValueError(f"Error when invoking function {name} with arguments {kwargs} with error message {e}")
        else: 
            raise ValueError(f"Function {name} is not registered.")
    
    async def ainvoke(self, name, kwargs):
        """
        Asynchronously invoke a registered function with the provided arguments.

        Parameters:
            name (str): The name of the function to invoke.
            kwargs (dict): The arguments to pass to the function.

        Returns:
            Any: The result of invoking the function asynchronously.

        """
        if self._name_existed(name):
            function = self.registry[name]["function"]
            try:
                if asyncio.iscoroutinefunction(function):
                    return await function(**kwargs)
                else:
                    return function(**kwargs)
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
        
    def register_tools(self, tools, functions, update=False, new=False, prefix=None, postfix=None):
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
        funcs = l_call(range(len(tools)), lambda i: self._from_tool(tools[i], functions[i]))
        l_call(range(len(tools)), lambda i: self._register_function(funcs[i][0], funcs[i][1], update=update, new=new, prefix=prefix, postfix=postfix))