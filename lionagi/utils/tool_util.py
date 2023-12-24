from abc import ABC, abstractmethod

class BaseTool(ABC):
    def __init__(self):
        self.logger = BaseLogger.get_logger(self.__class__.__name__)

    @abstractmethod
    def initialize(self, *args, **kwargs):
        """Initialize the tool with necessary parameters."""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the main functionality of the tool."""
        pass

    @abstractmethod
    def shutdown(self):
        """Perform any cleanup necessary and shut down the tool."""
        pass

    def __enter__(self):
        """Prepare the tool for context management."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up after context management."""
        self.shutdown()
        if exc_type:
            self.logger.error(f"Exception in {self.__class__.__name__}: {exc_val}", exc_info=True)

import inspect
import functools

def openai_tool_schema_decorator(required_params=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        function_name = func.__name__
        function_description = func.__doc__ or "No description provided."

        params = inspect.signature(func).parameters
        parameters = {}
        for name, param in params.items():
            if name == 'self':
                continue
            parameters[name] = {
                "type": "string",  # Simplified for the example
                "description": f"Parameter {name}"
            }

        tool_schema = {
            "type": "function",
            "function": {
                "name": function_name,
                "description": function_description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required_params or list(parameters.keys())
                },
            }
        }

        wrapper.tool_schema = tool_schema
        return wrapper
    return decorator

@openai_tool_schema_decorator(required_params=["str_or_query_bundle"])
def query_lionagi_codebase(str_or_query_bundle, optional_param="default"):
    """
    Perform a query to a QA bot with access to a vector index 
    built with package lionagi codebase.
    """
    return f"Querying with: {str_or_query_bundle}"

# Accessing the generated schema
print(query_lionagi_codebase.tool_schema)

{
    "type": "function",
    "function": {
        "name": "query_lionagi_codebase",
        "description": "Perform a query to a QA bot with access to a vector index built with package lionagi codebase.",
        "parameters": {
            "type": "object",
            "properties": {
                "str_or_query_bundle": {
                    "type": "string",
                    "description": "Parameter str_or_query_bundle"
                },
                "optional_param": {
                    "type": "string",
                    "description": "Parameter optional_param"
                }
            },
            "required": ["str_or_query_bundle"]
        }
    }
}


import asyncio
import logging

class ToolManager:
    def __init__(self):
        self.registry = {}

    def register_tools(self, tools):
        for name, tool_obj in tools.items():
            if not isinstance(tool_obj, BaseTool):
                raise TypeError(f"Tool {name} must be an instance of BaseTool")
            self.registry[name] = tool_obj
            self.logger.info(f"Registered tool: {name}")

    def activate_tool(self, tool_name):
        if tool_name in self.registry:
            tool = self.registry[tool_name]
            tool.initialize()
            self.logger.info(f"Activated tool: {tool_name}")
        else:
            raise KeyError(f"Tool {tool_name} not registered")

    def deactivate_tool(self, tool_name):
        if tool_name in self.registry:
            tool = self.registry[tool_name]
            tool.shutdown()
            self.logger.info(f"Deactivated tool: {tool_name}")
        else:
            raise KeyError(f"Tool {tool_name} not registered")

    def invoke(self, tool_name, *args, **kwargs):
        if tool_name in self.registry:
            tool = self.registry[tool_name]
            try:
                return tool.execute(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                raise
        else:
            raise KeyError(f"Tool {tool_name} not registered")

    async def ainvoke(self, tool_name, *args, **kwargs):
        if tool_name in self.registry:
            tool = self.registry[tool_name]
            try:
                if asyncio.iscoroutinefunction(tool.execute):
                    # Asynchronous execution
                    return await tool.execute(*args, **kwargs)
                else:
                    # Synchronous execution, but within an async context
                    return await asyncio.to_thread(tool.execute, *args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error executing tool {tool_name} asynchronously: {e}", exc_info=True)
                raise
        else:
            raise KeyError(f"Tool {tool_name} not registered")



"""
# ToolManager class with integrated logging
class ToolManager:
    def __init__(self):
        self.logger = BaseLogger.get_logger("ToolManager")
        self.registry = {}

    def register_tool(self, name, tool):
        if not isinstance(tool, BaseTool):
            raise ValueError("Invalid tool type. Must be a subclass of BaseTool.")
        self.registry[name] = tool
        self.logger.info(f"Tool registered: {name}")

    def execute_tool(self, name, *args, **kwargs):
        if name not in self.registry:
            self.logger.error(f"Tool {name} not found.")
            raise ValueError(f"Tool {name} not found.")
        tool = self.registry[name]
        self.logger.info(f"Executing tool: {name}")
        return tool.execute(*args, **kwargs)

# Example tool implementation
class MultiplyTool(BaseTool):
    def initialize(self):
        self.logger.info("MultiplyTool initialized")

    def execute(self, x, y):
        self.logger.info(f"Multiplying {x} and {y}")
        return x * y

    def shutdown(self):
        self.logger.info("MultiplyTool shutdown")

# Example usage
tool_manager = ToolManager()
multiply_tool = MultiplyTool()
tool_manager.register_tool("multiplier", multiply_tool)
result = tool_manager.execute_tool("multiplier", 3, 4)
print(f"Result: {result}")

"""