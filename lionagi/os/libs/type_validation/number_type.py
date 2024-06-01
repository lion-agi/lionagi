def check_number_field(x, fix_=True, **kwargs):
    if not isinstance(x, (int, float)):
        if fix_:
            try:
                return _fix_number_field(x, **kwargs)
            except Exception as e:
                raise e

        raise ValueError(
            f"Default value for NUMERIC must be an int or float, got {type(x).__name__}"
        )
    return x


def _fix_number_field(x, *args, **kwargs):
    try:
        x = to_num(x, *args, **kwargs)
        if isinstance(x, (int, float)):
            return x
        raise ValueError(f"Failed to convert {x} into a numeric value")
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into a numeric value") from e
