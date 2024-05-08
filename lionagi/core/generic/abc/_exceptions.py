class LionAGIError(Exception):
    """Base class for all exceptions in the LionAGI system."""

    def __init__(self, message=None):
        if message is None:
            message = "An unspecified error occurred in the LionAGI system."
        super().__init__(message)


class LionValueError(LionAGIError):
    """Exception raised for errors in the input value."""

    def __init__(self, message=None):
        if message is None:
            message = "An error occurred in the input value."
        super().__init__(message)


class LionTypeError(LionAGIError):
    """Exception raised for type mismatch or type checking errors."""

    def __init__(self, message=None):
        if message is None:
            message = "Item must be identifiable, `ln_id` or `Component`"
        super().__init__(message)


class LionItemError(LionAGIError):
    """Base class for exceptions related to LionAGI items."""

    def __init__(self, item, message=None):
        if message is None:
            message = "An error occurred with the specified item."
        super().__init__(f"{message} Item: '{item}'.")


class ItemNotFoundError(LionItemError):
    """Exception raised when a specified item is not found."""

    def __init__(self, item):
        super().__init__(item, "Item not found.")


class ItemInvalidError(LionItemError):
    """Exception raised when an invalid item is used in an operation."""

    def __init__(self, item):
        super().__init__(item, "The item is invalid for this operation.")


class LionFieldError(LionAGIError):
    """Exception raised for errors in field validation."""

    def __init__(self, field, message=None):
        if message is None:
            message = "An error occurred with the specified field."
        super().__init__(f"{message} Field: '{field}'.")


class LionOperationError(LionAGIError):
    """Base class for exceptions related to operational failures."""

    def __init__(self, operation, message=None):
        if message is None:
            message = "An operation failed."
        super().__init__(f"{message} Operation: '{operation}'.")


class ConcurrencyError(LionOperationError):
    """Exception raised for errors due to concurrency issues."""

    def __init__(self, operation=None):
        if operation is None:
            operation = "a concurrent operation"
        super().__init__(operation, "A concurrency error occurred during")


class ResourceLimitExceededError(LionOperationError):
    """Exception raised when a resource limit is exceeded."""

    def __init__(self, resource, limit):
        super().__init__(resource, f"Resource limit exceeded. Limit: {limit}")


class TimeoutError(LionOperationError):
    """Exception raised when an operation times out."""

    def __init__(self, operation, timeout):
        super().__init__(operation, f"Operation timed out after {timeout} seconds.")
