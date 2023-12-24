from abc import ABC, abstractmethod
import logging

class BaseTool(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

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
