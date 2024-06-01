def check_bool_field(x, fix_=True):
    if not isinstance(x, bool):
        if fix_:
            try:
                return _fix_bool_field(x)
            except Exception as e:
                raise e

        raise ValueError(
            f"Default value for BOOLEAN must be a bool, got {type(x).__name__}"
        )
    return x


def _fix_bool_field(x):
    try:
        x = strip_lower(to_str(x))
        if x in ["true", "1", "correct", "yes"]:
            return True

        elif x in ["false", "0", "incorrect", "no", "none", "n/a"]:
            return False

        raise ValueError(f"Failed to convert {x} into a boolean value")
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into a boolean value") from e
