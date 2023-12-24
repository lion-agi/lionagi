from .basetool import BaseTool

class MultiplyTool(BaseTool):
    def initialize(self):
        """Initialize the MultiplyTool."""
        self.logger.info("Initializing MultiplyTool")

    def execute(self, x, y):
        """Multiply two numbers.

        Args:
            x (float/int): The first number.
            y (float/int): The second number.

        Returns:
            float/int: The product of x and y.
        """
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise ValueError("Both x and y must be numbers")
        self.logger.info(f"Multiplying {x} and {y}")
        return x * y

    def shutdown(self):
        """Shutdown the MultiplyTool."""
        self.logger.info("Shutting down MultiplyTool")
