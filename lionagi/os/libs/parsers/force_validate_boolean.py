from lionagi.os.libs.data_handlers import strip_lower


def force_validate_boolean(x):
    """
    Forcefully validates and converts the input into a boolean value.

    Args:
        x (Any): The input to be converted to boolean.

    Returns:
        bool: The boolean representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a boolean value.

    Examples:
        >>> force_validate_boolean("true")
        True
        >>> force_validate_boolean("false")
        False
        >>> force_validate_boolean("yes")
        True
        >>> force_validate_boolean("no")
        False
        >>> force_validate_boolean(True)
        True
        >>> force_validate_boolean("1")
        True
        >>> force_validate_boolean("0")
        False
    """
    if isinstance(x, bool):
        return x

    if strip_lower(x) in ["true", "1", "correct", "yes"]:
        return True

    elif strip_lower(x) in ["false", "0", "incorrect", "no", "none", "n/a"]:
        return False

    raise ValueError(f"Failed to convert {x} into a boolean value")
