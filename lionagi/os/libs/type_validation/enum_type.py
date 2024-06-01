def _fix_enum_field(x, choices, **kwargs):
    try:
        x = to_str(x)
        return StringMatch.choose_most_similar(x, choices, **kwargs)
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into one of the choices") from e


def check_enum_field(x, choices, fix_=True, **kwargs):
    same_dtype, dtype_ = is_same_dtype(choices, return_dtype=True)
    if not same_dtype:
        raise ValueError(
            f"Field type ENUM requires all choices to be of the same type, got {choices}"
        )

    if not isinstance(x, dtype_):
        raise ValueError(
            f"Default value for ENUM must be an instance of the {dtype_.__name__}, got {type(x).__name__}"
        )

    if x not in choices:
        if fix_:
            try:
                return _fix_enum_field(x, choices, **kwargs)
            except Exception as e:
                raise e
        raise ValueError(
            f"Default value for ENUM must be one of the {choices}, got {x}"
        )

    return x
