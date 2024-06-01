from ..data_handlers import strip_lower


def force_validate_boolean(x):
    if not isinstance(x, bool):
        return _force_validate_boolean(x)
    return x


def _force_validate_boolean(x):
    try:
        x = strip_lower(x)
        if x in ["true", "1", "correct", "yes"]:
            return True

        elif x in ["false", "0", "incorrect", "no", "none", "n/a"]:
            return False

        raise ValueError(f"Failed to convert {x} into a boolean value")
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into a boolean value") from e
