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


def check_enum_field(x, choices, fix_=True, **kwargs):
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


# # File: field_validators.py

# from functools import wraps
# from lionagi.libs import convert, StringMatch
# from typing import Any, Callable, Dict, Tuple

# def validator(fix_func: Callable[..., Any], expected_type: Tuple[type, ...], type_name: str):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(x, *args, fix_=True, **kwargs):
#             if not isinstance(x, expected_type):
#                 if fix_:
#                     try:
#                         return fix_func(x, *args, **kwargs)
#                     except Exception as e:
#                         raise ValueError(f"Failed to fix field of type {type_name}") from e
#                 raise ValueError(f"Default value for {type_name} must be one of {expected_type}, got {type(x).__name__}")
#             return x
#         return wrapper
#     return decorator

# @validator(fix_func=lambda x, **kwargs: _fix_enum_field(x, kwargs.get('choices', []), **kwargs), expected_type=(object,), type_name="ENUM")
# def check_enum_field(x, choices, **kwargs):
#     if not choices:
#         raise ValueError("Field type ENUM requires 'choices' parameter.")
#     same_dtype, dtype_ = convert.is_same_dtype(choices, return_dtype=True)
#     if not same_dtype or not isinstance(x, dtype_):
#         raise ValueError(f"Field type ENUM requires all choices to be of the same type and the default value to match, got {type(x).__name__}")
#     if x not in choices:
#         raise ValueError(f"Default value for ENUM must be one of the {choices}, got {x}")
#     return x

# @validator(fix_func=_fix_number_field, expected_type=(int, float), type_name="NUMERIC")
# def check_number_field(x, **kwargs):
#     return x

# @validator(fix_func=_fix_bool_field, expected_type=(bool,), type_name="BOOLEAN")
# def check_bool_field(x):
#     return x

# @validator(fix_func=_fix_str_field, expected_type=(str,), type_name="STRING")
# def check_str_field(x, **kwargs):
#     return x

# def _fix_number_field(x, **kwargs):
#     try:
#         return convert.to_num(convert.to_str(x), **kwargs)
#     except Exception as e:
#         raise ValueError(f"Failed to convert {x} into a numeric value") from e

# def _fix_bool_field(x):
#     try:
#         x = convert.to_str(x).lower()
#         if x in ["true", "1", "correct", "yes"]:
#             return True
#         elif x in ["false", "0", "incorrect", "no", "none", "n/a"]:
#             return False
#         else:
#             raise ValueError()
#     except:
#         raise ValueError(f"Failed to convert {x} into a boolean value")

# def _fix_str_field(x):
#     return convert.to_str(x)

# def _fix_enum_field(x, choices, **kwargs):
#     x = convert.to_str(x)
#     return StringMatch.choose_most_similar(x, choices, **kwargs)

# validation_funcs = {
#     "number": check_number_field,
#     "bool": check_bool_field,
#     "str": check_str_field,
#     "enum": check_enum_field,
# }
