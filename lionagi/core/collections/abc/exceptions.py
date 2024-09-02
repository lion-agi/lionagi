from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.LionAGIError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class LionAGIError(Exception):
    """Base class for all exceptions in the LionAGI system."""

    def __init__(self, message=None):
        if message is None:
            message = "An unspecified error occurred in the LionAGI system."
        super().__init__(message)


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.LionValueError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class LionValueError(LionAGIError):
    """Exception raised for errors in the input value."""

    def __init__(self, message=None):
        if message is None:
            message = "An error occurred in the input value."
        super().__init__(message)


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.LionTypeError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class LionTypeError(LionAGIError):
    """Exception raised for type mismatch or type checking errors."""

    def __init__(self, message=None):
        if message is None:
            message = "Item must be identifiable, `ln_id` or `Component`"
        super().__init__(message)


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.LionItemError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class LionItemError(LionAGIError):
    """Base class for exceptions related to LionAGI items."""

    def __init__(self, item, message=None):
        if message is None:
            message = "An error occurred with the specified item."
        super().__init__(f"{message} Item: '{item}'.")


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.ItemNotFoundError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class ItemNotFoundError(LionItemError):
    """Exception raised when a specified item is not found."""

    def __init__(self, item):
        super().__init__(item, "Item not found.")


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.ItemInvalidError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class ItemInvalidError(LionItemError):
    """Exception raised when an invalid item is used in an operation."""

    def __init__(self, item):
        super().__init__(item, "The item is invalid for this operation.")


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.FieldError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement=None,
    ),
    category=DeprecationWarning,
)
class FieldError(LionAGIError):
    """Exception raised for errors in field validation."""

    def __init__(self, field, message=None):
        if message is None:
            message = "An error occurred with the specified field."
        super().__init__(f"{message}: {field}.")


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.LionOperationError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class LionOperationError(LionAGIError):
    """Base class for exceptions related to operational failures."""

    def __init__(self, operation, message=None):
        if message is None:
            message = "An operation failed."
        super().__init__(f"{message} Operation: '{operation}'.")


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.ConcurrencyError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement=None,
    ),
    category=DeprecationWarning,
)
class ConcurrencyError(LionOperationError):
    """Exception raised for errors due to concurrency issues."""

    def __init__(self, operation=None):
        if operation is None:
            operation = "a concurrent operation"
        super().__init__(operation, "A concurrency error occurred during")


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.RelationError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class RelationError(LionAGIError):
    """Exception raised for errors in relation operations."""

    def __init__(self, message=None):
        if message is None:
            message = "Nodes are not related."
        super().__init__(message)


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.ActionError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class ActionError(LionAGIError):
    """Exception raised for errors in action operations."""

    def __init__(self, message=None):
        if message is None:
            message = "An error occurred with the specified action."
        super().__init__(message)


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.ModelLimitExceededError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class ModelLimitExceededError(LionOperationError):
    """Exception raised when a resource limit is exceeded."""

    def __init__(self, message=None):
        if message is None:
            message = "The model limit has been exceeded."
        super().__init__("Model", message)


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.TimeoutError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement=None,
    ),
    category=DeprecationWarning,
)
class TimeoutError(LionOperationError):
    """Exception raised when an operation times out."""

    def __init__(self, operation, timeout):
        super().__init__(operation, f"Operation timed out after {timeout} seconds.")


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.exceptions.ServiceError",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement=None,
    ),
    category=DeprecationWarning,
)
class ServiceError(LionAGIError):
    """Exception raised for errors in endpoint configuration."""

    def __init__(self, message, errors=None):
        super().__init__(message, errors)

    @classmethod
    def unavailable(cls, endpoint, service, err_msg=None):
        msg = f"{endpoint} is currently unavailable"
        if err_msg:
            msg += f": {err_msg}"
        else:
            msg += f" for {service.__class__.__name__}"
        return cls(msg)
