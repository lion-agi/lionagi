import logging
from abc import ABC, abstractmethod

import logging
import logging.config
import os

# Basic configuration for the logging system
def setup_logging():
    logging_conf = {
        "version": 1,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": logging.INFO,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": logging.INFO,
        },
    }

    logging.config.dictConfig(logging_conf)

setup_logging()



# Global logging setup
def setup_global_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] - %(name)s - %(message)s')

# Call this at the start of your application
setup_global_logging()

# BaseLogger for centralized logger creation
class BaseLogger:
    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

# BaseTool class with integrated logging
class BaseTool(ABC):
    def __init__(self):
        self.logger = BaseLogger.get_logger(self.__class__.__name__)

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass

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
