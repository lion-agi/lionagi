import json
from ._to_list import to_list
from ._to_dict import to_dict


def to_str(
    input_, /, use_model_dump: bool = True, strip_lower: bool = False, **kwargs
) -> str:
    """
    Convert the input to a string representation.

    If the input is a list, recursively converts each element to a string
    and joins them with a comma. If the input is a dictionary, converts it
    to a JSON string. If the input is a string, optionally strips and
    converts it to lowercase.

    Args:
        input_: The input to be converted to a string.
        use_model_dump (bool, optional): Whether to use a custom model dump
            function. Defaults to True.
        strip_lower (bool, optional): Whether to strip and convert the
            string to lowercase. Defaults to False.
        **kwargs: Additional keyword arguments to pass to json.dumps.

    Returns:
        str: The string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a string.
    """
    if isinstance(input_, list):
        input_ = to_list(input_)
        return ", ".join(
            [
                to_str(
                    item,
                    use_model_dump=use_model_dump,
                    strip_lower=strip_lower,
                    **kwargs,
                )
                for item in input_
            ]
        )

    return _to_str(
        input_, use_model_dump=use_model_dump, strip_lower=strip_lower, **kwargs
    )


def _to_str(
    input_, /, use_model_dump: bool = None, strip_lower: bool = None, **kwargs
) -> str:
    """
    Helper function to convert the input to a string representation.

    Args:
        input_: The input to be converted to a string.
        use_model_dump (bool, optional): Whether to use a custom model dump
            function. Defaults to None.
        strip_lower (bool, optional): Whether to strip and convert the string
            to lowercase. Defaults to None.
        **kwargs: Additional keyword arguments to pass to json.dumps.

    Returns:
        str: The string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a string.
    """
    if isinstance(input_, dict):
        input_ = json.dumps(input_, **kwargs)

    if isinstance(input_, str):
        return input_.strip().lower() if strip_lower else input_

    try:
        dict_ = to_dict(input_, as_list=False, use_model_dump=use_model_dump)
        return (
            json.dumps(dict_, **kwargs).strip().lower()
            if strip_lower
            else json.dumps(dict_, **kwargs)
        )
    except Exception:
        try:
            return str(input_).strip().lower() if strip_lower else str(input_)
        except Exception as e:
            raise ValueError(
                f"Could not convert input_ to string: {input_}, Error: {e}"
            )


def strip_lower(input_: str, /, **kwargs) -> str:
    """
    Convert the input to a stripped and lowercase string representation.

    Args:
        input_ (str): The input string to be processed.
        **kwargs: Additional keyword arguments to pass to to_str.

    Returns:
        str: The stripped and lowercase string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a string.
    """
    try:
        return to_str(input_, **kwargs).strip().lower()
    except Exception as e:
        raise ValueError(f"Could not convert input_ to string: {input_}, Error: {e}")
