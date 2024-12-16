import json
from collections.abc import Callable, Mapping
from typing import Any, Literal

from pydantic_core import PydanticUndefined, PydanticUndefinedType

from lionagi.libs.constants import UNDEFINED, UndefinedType

from ..xml.convert import dict_to_xml
from .to_dict import to_dict


def _serialize_as(
    input_,
    /,
    *,
    serialize_as: Literal["json", "xml"],
    strip_lower: bool = False,
    chars: str | None = None,
    str_type: Literal["json", "xml"] | None = None,
    use_model_dump: bool = False,
    str_parser: Callable[[str], dict[str, Any]] | None = None,
    parser_kwargs: dict = {},
    **kwargs: Any,
) -> str:
    try:
        dict_ = to_dict(
            input_,
            use_model_dump=use_model_dump,
            str_type=str_type,
            suppress=True,
            parser=str_parser,
            **parser_kwargs,
        )
        if any((str_type, chars)):
            str_ = json.dumps(dict_)
            str_ = _process_string(str_, strip_lower=strip_lower, chars=chars)
            dict_ = json.loads(str_)

        if serialize_as == "json":
            return json.dumps(dict_, **kwargs)

        if serialize_as == "xml":
            return dict_to_xml(dict_, **kwargs)
    except Exception as e:
        raise ValueError(
            f"Failed to serialize input of {type(input_).__name__} "
            f"into <{str_type}>"
        ) from e


def _to_str_type(input_: Any, /) -> str:
    if input_ in [set(), [], {}]:
        return ""

    if isinstance(input_, type(None) | UndefinedType | PydanticUndefinedType):
        return ""

    if isinstance(input_, bytes | bytearray):
        return input_.decode("utf-8", errors="replace")

    if isinstance(input_, str):
        return input_

    if isinstance(input_, Mapping):
        return json.dumps(dict(input_))

    try:
        return str(input_)
    except Exception as e:
        raise ValueError(
            f"Could not convert input of type <{type(input_).__name__}> "
            "to string"
        ) from e


def to_str(
    input_: Any,
    /,
    *,
    strip_lower: bool = False,
    chars: str | None = None,
    str_type: Literal["json", "xml"] | None = None,
    serialize_as: Literal["json", "xml"] | None = None,
    use_model_dump: bool = False,
    str_parser: Callable[[str], dict[str, Any]] | None = None,
    parser_kwargs: dict = {},
    **kwargs: Any,
) -> str:
    """Convert any input to its string representation.

    Handles various input types, with options for serialization and formatting.

    Args:
        input_: The input to convert to a string.
        strip_lower: If True, strip whitespace and convert to lowercase.
        chars: Specific characters to strip from the result.
        str_type: Type of string input ("json" or "xml") if applicable.
        serialize_as: Output serialization format ("json" or "xml").
        use_model_dump: Use model_dump for Pydantic models if available.
        str_parser: Custom parser function for string inputs.
        parser_kwargs: Additional keyword arguments for the parser.
        **kwargs: Additional arguments passed to json.dumps or serialization.

    Returns:
        str: The string representation of the input.

    Raises:
        ValueError: If serialization or conversion fails.

    Examples:
        >>> to_str(123)
        '123'
        >>> to_str("  HELLO  ", strip_lower=True)
        'hello'
        >>> to_str({"a": 1}, serialize_as="json")
        '{"a": 1}'
        >>> to_str({"a": 1}, serialize_as="xml")
        '<root><a>1</a></root>'
    """

    if serialize_as:
        return _serialize_as(
            input_,
            serialize_as=serialize_as,
            strip_lower=strip_lower,
            chars=chars,
            str_type=str_type,
            use_model_dump=use_model_dump,
            str_parser=str_parser,
            parser_kwargs=parser_kwargs,
            **kwargs,
        )

    str_ = _to_str_type(input_, **kwargs)
    if any((strip_lower, chars)):
        str_ = _process_string(str_, strip_lower=strip_lower, chars=chars)
    return str_


def _process_string(s: str, strip_lower: bool, chars: str | None) -> str:
    if s in [UNDEFINED, PydanticUndefined, None, [], {}]:
        return ""

    if strip_lower:
        s = s.lower()
        s = s.strip(chars) if chars is not None else s.strip()
    return s


def strip_lower(
    input_: Any,
    /,
    *,
    chars: str | None = None,
    str_type: Literal["json", "xml"] | None = None,
    serialize_as: Literal["json", "xml"] | None = None,
    use_model_dump: bool = False,
    str_parser: Callable[[str], dict[str, Any]] | None = None,
    parser_kwargs: dict = {},
    **kwargs: Any,
) -> str:
    """
    Convert input to stripped and lowercase string representation.

    This function is a convenience wrapper around to_str that always
    applies stripping and lowercasing.

    Args:
        input_: The input to convert to a string.
        use_model_dump: If True, use model_dump for Pydantic models.
        chars: Characters to strip from the result.
        **kwargs: Additional arguments to pass to to_str.

    Returns:
        Stripped and lowercase string representation of the input.

    Raises:
        ValueError: If conversion fails.

    Example:
        >>> strip_lower("  HELLO WORLD  ")
        'hello world'
    """
    return to_str(
        input_,
        strip_lower=True,
        chars=chars,
        str_type=str_type,
        serialize_as=serialize_as,
        use_model_dump=use_model_dump,
        str_parser=str_parser,
        parser_kwargs=parser_kwargs,
        **kwargs,
    )
