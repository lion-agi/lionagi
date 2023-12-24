import asyncio
import logging
from .basetool import BaseTool

class ToolManager:
    def __init__(self):
        self.logger = logging.getLogger("ToolManager")
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