import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from enum import Enum
from functools import partial
from typing import Any, Literal

from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType

from lionagi.libs.constants import UndefinedType

from ..json.parse import fuzzy_parse_json
from ..xml.convert import xml_to_dict


def to_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool = True,
    fuzzy_parse: bool = False,
    suppress: bool = False,
    str_type: Literal["json", "xml"] | None = "json",
    parser: Callable[[str], Any] | None = None,
    recursive: bool = False,
    max_recursive_depth: int = None,
    recursive_python_only: bool = True,
    use_enum_values: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Convert various input types to a dictionary, with optional recursive processing.

    Args:
        input_: The input to convert.
        use_model_dump: Use model_dump() for Pydantic models if available.
        fuzzy_parse: Use fuzzy parsing for string inputs.
        suppress: Return empty dict on errors if True.
        str_type: Input string type ("json" or "xml").
        parser: Custom parser function for string inputs.
        recursive: Enable recursive conversion of nested structures.
        max_recursive_depth: Maximum recursion depth (default 5, max 10).
        recursive_python_only: If False, attempts to convert custom types recursively.
        use_enum_values: Use enum values instead of names.
        **kwargs: Additional arguments for parsing functions.

    Returns:
        dict[str, Any]: A dictionary derived from the input.

    Raises:
        ValueError: If parsing fails and suppress is False.

    Examples:
        >>> to_dict({"a": 1, "b": [2, 3]})
        {'a': 1, 'b': [2, 3]}
        >>> to_dict('{"x": 10}', str_type="json")
        {'x': 10}
        >>> to_dict({"a": {"b": {"c": 1}}}, recursive=True, max_recursive_depth=2)
        {'a': {'b': {'c': 1}}}
    """

    try:
        if recursive:
            return recursive_to_dict(
                input_,
                use_model_dump=use_model_dump,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                max_recursive_depth=max_recursive_depth,
                recursive_custom_types=not recursive_python_only,
                use_enum_values=use_enum_values,
                **kwargs,
            )

        return _to_dict(
            input_,
            fuzzy_parse=fuzzy_parse,
            parser=parser,
            str_type=str_type,
            use_model_dump=use_model_dump,
            use_enum_values=use_enum_values,
            **kwargs,
        )
    except Exception as e:
        if suppress or input_ == "":
            return {}
        raise e


def recursive_to_dict(
    input_: Any,
    /,
    *,
    max_recursive_depth: int = None,
    recursive_custom_types: bool = False,
    **kwargs: Any,
) -> Any:

    if not isinstance(max_recursive_depth, int):
        max_recursive_depth = 5
    else:
        if max_recursive_depth < 0:
            raise ValueError(
                "max_recursive_depth must be a non-negative integer"
            )
        if max_recursive_depth == 0:
            return input_
        if max_recursive_depth > 10:
            raise ValueError(
                "max_recursive_depth must be less than or equal to 10"
            )

    return _recur_to_dict(
        input_,
        max_recursive_depth=max_recursive_depth,
        current_depth=0,
        recursive_custom_types=recursive_custom_types,
        **kwargs,
    )


def _recur_to_dict(
    input_: Any,
    /,
    *,
    max_recursive_depth: int,
    current_depth: int = 0,
    recursive_custom_types: bool = False,
    **kwargs: Any,
) -> Any:

    if current_depth >= max_recursive_depth:
        return input_

    if isinstance(input_, str):
        try:
            # Attempt to parse the string
            parsed = _to_dict(input_, **kwargs)
            # Recursively process the parsed result
            return _recur_to_dict(
                parsed,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                **kwargs,
            )
        except Exception:
            # Return the original string if parsing fails
            return input_

    elif isinstance(input_, dict):
        # Recursively process dictionary values
        return {
            key: _recur_to_dict(
                value,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                **kwargs,
            )
            for key, value in input_.items()
        }

    elif isinstance(input_, (list, tuple, set)):
        # Recursively process list or tuple elements
        processed = [
            _recur_to_dict(
                element,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                **kwargs,
            )
            for element in input_
        ]
        return type(input_)(processed)

    elif isinstance(input_, type) and issubclass(input_, Enum):
        try:
            obj_dict = _to_dict(input_, **kwargs)
            return _recur_to_dict(
                obj_dict,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                **kwargs,
            )
        except Exception:
            return input_

    elif recursive_custom_types:
        # Process custom classes if enabled
        try:
            obj_dict = _to_dict(input_, **kwargs)
            return _recur_to_dict(
                obj_dict,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                **kwargs,
            )
        except Exception:
            return input_

    else:
        # Return the input as is for other data types
        return input_


def _enum_to_dict(input_, /, use_enum_values: bool = True):
    dict_ = dict(input_.__members__).copy()
    if use_enum_values:
        return {key: value.value for key, value in dict_.items()}
    return dict_


def _str_to_dict(
    input_: str,
    /,
    fuzzy_parse: bool = False,
    str_type: Literal["json", "xml"] | None = "json",
    parser: Callable[[str], Any] | None = None,
    remove_root: bool = False,
    root_tag: str = "root",
    **kwargs: Any,
):
    """
    kwargs for parser
    """
    if not parser:
        if str_type == "xml" and not parser:
            parser = partial(
                xml_to_dict, remove_root=remove_root, root_tag=root_tag
            )

        elif fuzzy_parse:
            parser = fuzzy_parse_json
        else:
            parser = json.loads

    return parser(input_, **kwargs)


def _na_to_dict(input_: type[None] | UndefinedType | PydanticUndefinedType, /):
    return {}


def _model_to_dict(input_: Any, /, use_model_dump=True, **kwargs):
    """
    kwargs: built-in serialization methods kwargs
    accepted built-in serialization methods:
        - mdoel_dump
        - to_dict
        - to_json
        - dict
        - json
    """

    if use_model_dump and hasattr(input_, "model_dump"):
        return input_.model_dump(**kwargs)

    methods = (
        "to_dict",
        "to_json",
        "json",
        "dict",
    )
    for method in methods:
        if hasattr(input_, method):
            result = getattr(input_, method)(**kwargs)
            return json.loads(result) if isinstance(result, str) else result

    if hasattr(input_, "__dict__"):
        return input_.__dict__

    try:
        return dict(input_)
    except Exception as e:
        raise ValueError(f"Unable to convert input to dictionary: {e}")


def _set_to_dict(input_: set, /) -> dict:
    return {v: v for v in input_}


def _iterable_to_dict(input_: Iterable, /) -> dict:
    return {idx: v for idx, v in enumerate(input_)}


def _to_dict(
    input_: Any,
    /,
    *,
    fuzzy_parse: bool = False,
    str_type: Literal["json", "xml"] | None = "json",
    parser: Callable[[str], Any] | None = None,
    remove_root: bool = False,
    root_tag: str = "root",
    use_model_dump: bool = True,
    use_enum_values: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:

    if isinstance(input_, set):
        return _set_to_dict(input_)

    if isinstance(input_, type) and issubclass(input_, Enum):
        return _enum_to_dict(input_, use_enum_values=use_enum_values)

    if isinstance(input_, Mapping):
        return dict(input_)

    if isinstance(input_, type(None) | UndefinedType | PydanticUndefinedType):
        return _na_to_dict(input_)

    if isinstance(input_, str):
        return _str_to_dict(
            input_,
            fuzzy_parse=fuzzy_parse,
            str_type=str_type,
            parser=parser,
            remove_root=remove_root,
            root_tag=root_tag,
            **kwargs,
        )

    if isinstance(input_, BaseModel) or not isinstance(input_, Sequence):
        return _model_to_dict(input_, use_model_dump=use_model_dump, **kwargs)

    if isinstance(input_, Iterable):
        return _iterable_to_dict(input_)

    return dict(input_)
