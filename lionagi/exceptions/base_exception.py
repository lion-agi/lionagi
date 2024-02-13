import logging

# Configure logging
logging.basicConfig(filename='lionagi_tool_manager.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Custom exception classes
class BaseException(Exception):
    """Base class for exceptions in the LionAGI tool manager."""
    pass

class APIException(BaseException):
    """Exception raised for errors in communication with external API services."""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors

class ActionException(BaseException):
    def __init__(self, message, errors=None):
        """Exception raised for errors in action invocation."""
        super().__init__(message)
        self.errors = errors

class InferenceException(BaseException):
    """Exception raised for errors in inference."""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors
