from lionagi.libs import convert, StringMatch


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


def check_str_field(x, *args, fix_=True, **kwargs):
    if not isinstance(x, str):
        if fix_:
            try:
                return _fix_str_field(x, *args, **kwargs)
            except Exception as e:
                raise e

        raise ValueError(
            f"Default value for STRING must be a str, got {type(x).__name__}"
        )
    return x


def check_enum_field(x, model_fields_, choices, fix_=True, **kwargs):
    if "choices" not in model_fields_:
        raise ValueError(
            "Field type ENUM requires the 'choices' attribute to be specified."
        )

    same_dtype, dtype_ = convert.is_same_dtype(choices, return_dtype=True)
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


def _fix_number_field(x, *args, **kwargs):
    try:
        x = convert.to_str(x)
        x = convert.to_num(x, *args, **kwargs)
        if isinstance(x, (int, float)):
            return x
        raise ValueError(f"Failed to convert {x} into a numeric value")
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into a numeric value") from e


def _fix_bool_field(x):
    try:
        x = convert.to_str(x)
        if (
            convert.strip_lower(x) in ["true", "1", "correct", "yes"]
            or convert.to_num(x) == 1
        ):
            return True
        elif (
            convert.strip_lower(x) in ["false", "0", "incorrect", "no", "none", "n/a"]
            or convert.to_num(x) == 0
        ):
            return False
        raise ValueError(f"Failed to convert {x} into a boolean value")
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into a boolean value") from e


def _fix_str_field(x):
    try:
        x = convert.to_str(x)
        if isinstance(x, str):
            return x
        raise ValueError(f"Failed to convert {x} into a string value")
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into a string value") from e


def _fix_enum_field(x, choices, **kwargs):
    try:
        x = convert.to_str(x)
        return StringMatch.choose_most_similar(x, choices, **kwargs)
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into one of the choices") from e


validation_funcs = {
    "number": check_number_field,
    "bool": check_bool_field,
    "str": check_str_field,
    "enum": check_enum_field,
}
