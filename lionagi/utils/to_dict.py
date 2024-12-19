from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from enum import Enum
from typing import Any, Literal, overload

from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType

from .fuzzy_parse_json import fuzzy_parse_json
from .undefined import UndefinedType


@overload
def to_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool = True,
    fuzzy_parse: bool = False,
    suppress: bool = False,
    str_type: Literal["json", "xml"] | None = "json",
    parser: Callable[[str], Any] | None = None,
    recursive: Literal[False] = False,
    max_recursive_depth: int | None = None,
    recursive_python_only: bool = True,
    use_enum_values: bool = False,
    remove_root: bool = False,
    root_tag: str = "root",
) -> dict[str, Any]: ...


@overload
def to_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool = True,
    fuzzy_parse: bool = False,
    suppress: bool = False,
    str_type: Literal["json", "xml"] | None = "json",
    parser: Callable[[str], Any] | None = None,
    recursive: Literal[True],
    max_recursive_depth: int | None = None,
    recursive_python_only: bool = True,
    use_enum_values: bool = False,
    remove_root: bool = False,
    root_tag: str = "root",
) -> Any: ...


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
    max_recursive_depth: int | None = None,
    recursive_python_only: bool = True,
    use_enum_values: bool = False,
    remove_root: bool = False,
    root_tag: str = "root",
) -> Any:
    try:
        if recursive:
            return recursive_to_dict(
                input_,
                use_model_dump=use_model_dump,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                max_recursive_depth=max_recursive_depth,
                recursive_python_only=recursive_python_only,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
        return _to_dict(
            input_,
            fuzzy_parse=fuzzy_parse,
            str_type=str_type,
            parser=parser,
            use_model_dump=use_model_dump,
            use_enum_values=use_enum_values,
            remove_root=remove_root,
            root_tag=root_tag,
        )
    except Exception:
        if suppress:
            return {}
        # Removed `or input_ == ""` so empty string raises ValueError
        raise


def recursive_to_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool,
    fuzzy_parse: bool,
    str_type: Literal["json", "xml"] | None,
    parser: Callable[[str], Any] | None,
    max_recursive_depth: int | None,
    recursive_python_only: bool,
    use_enum_values: bool,
    remove_root: bool,
    root_tag: str,
) -> Any:
    if max_recursive_depth is None:
        max_recursive_depth = 5
    if max_recursive_depth < 0:
        raise ValueError("max_recursive_depth must be a non-negative integer")
    if max_recursive_depth > 10:
        raise ValueError("max_recursive_depth must be <= 10")

    return _recur_to_dict(
        input_,
        max_recursive_depth=max_recursive_depth,
        current_depth=0,
        recursive_custom_types=not recursive_python_only,
        use_model_dump=use_model_dump,
        fuzzy_parse=fuzzy_parse,
        str_type=str_type,
        parser=parser,
        use_enum_values=use_enum_values,
        remove_root=remove_root,
        root_tag=root_tag,
    )


def _recur_to_dict(
    input_: Any,
    /,
    *,
    max_recursive_depth: int,
    current_depth: int,
    recursive_custom_types: bool,
    use_model_dump: bool,
    fuzzy_parse: bool,
    str_type: Literal["json", "xml"] | None,
    parser: Callable[[str], Any] | None,
    use_enum_values: bool,
    remove_root: bool,
    root_tag: str,
) -> Any:
    if current_depth >= max_recursive_depth:
        return input_

    if isinstance(input_, str):
        try:
            parsed = _to_dict(
                input_,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                use_model_dump=use_model_dump,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
            return _recur_to_dict(
                parsed,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                use_model_dump=use_model_dump,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
        except Exception:
            return input_

    elif isinstance(input_, dict):
        return {
            k: _recur_to_dict(
                v,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                use_model_dump=use_model_dump,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
            for k, v in input_.items()
        }

    elif isinstance(input_, (list, tuple, set)):
        processed = [
            _recur_to_dict(
                e,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                use_model_dump=use_model_dump,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
            for e in input_
        ]
        return type(input_)(processed)

    elif isinstance(input_, type) and issubclass(input_, Enum):
        try:
            obj_dict = _to_dict(
                input_,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                use_model_dump=use_model_dump,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
            return _recur_to_dict(
                obj_dict,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                use_model_dump=use_model_dump,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
        except Exception:
            return input_

    elif recursive_custom_types:
        try:
            obj_dict = _to_dict(
                input_,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                use_model_dump=use_model_dump,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
            return _recur_to_dict(
                obj_dict,
                max_recursive_depth=max_recursive_depth,
                current_depth=current_depth + 1,
                recursive_custom_types=recursive_custom_types,
                use_model_dump=use_model_dump,
                fuzzy_parse=fuzzy_parse,
                str_type=str_type,
                parser=parser,
                use_enum_values=use_enum_values,
                remove_root=remove_root,
                root_tag=root_tag,
            )
        except Exception:
            return input_

    return input_


def _enum_to_dict(input_: type[Enum], /, use_enum_values: bool) -> dict:
    members = dict(input_.__members__)
    return {
        k: (v.value if use_enum_values else v.name) for k, v in members.items()
    }


def _str_to_dict(
    input_: str,
    /,
    *,
    fuzzy_parse: bool,
    str_type: Literal["json", "xml"] | None,
    parser: Callable[[str], Any] | None,
    remove_root: bool,
    root_tag: str,
) -> dict[str, Any]:
    if parser:
        return parser(input_)

    if str_type == "xml":
        # Wrap in try-except to raise ValueError on parse errors
        try:
            import xmltodict

            parsed = xmltodict.parse(input_)
        except Exception as e:
            raise ValueError(f"Invalid XML: {e}") from e

        if remove_root and isinstance(parsed, dict) and len(parsed) == 1:
            parsed = next(iter(parsed.values()))
            if not isinstance(parsed, dict):
                parsed = {"value": parsed}
        else:
            if root_tag != "root":
                if isinstance(parsed, dict) and len(parsed) == 1:
                    old_root_key = next(iter(parsed.keys()))
                    contents = parsed[old_root_key]
                    parsed = {root_tag: contents}
                else:
                    parsed = {root_tag: parsed}

        if not isinstance(parsed, dict):
            parsed = {"value": parsed}
        return parsed

    # JSON
    if fuzzy_parse:
        return fuzzy_parse_json(input_)
    try:
        return json.loads(input_)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e


def _na_to_dict(input_: Any) -> dict[str, Any]:
    # Handle PydanticUndefinedType specifically
    if input_ is PydanticUndefinedType:
        return {}
    if isinstance(input_, (type(None), UndefinedType, PydanticUndefinedType)):
        return {}
    return {}


def _model_to_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool,
) -> dict[str, Any]:
    # If input is a BaseModel
    if isinstance(input_, BaseModel):
        if use_model_dump and hasattr(input_, "model_dump"):
            return input_.model_dump()

        methods = ("to_dict", "to_json", "json", "dict", "model_dump")
        for method in methods:
            if hasattr(input_, method):
                result = getattr(input_, method)()
                return (
                    json.loads(result) if isinstance(result, str) else result
                )

        if hasattr(input_, "__dict__"):
            return dict(input_.__dict__)

        try:
            return dict(input_)
        except Exception as e:
            raise ValueError(f"Unable to convert input to dictionary: {e}")
    else:
        # Non-BaseModel objects that reach here
        # Distinguish between Sequence and Iterable
        if isinstance(input_, Sequence) and not isinstance(input_, str):
            # If it's a sequence (like a list), we wouldn't be here,
            # because lists handled in _to_dict before calling _model_to_dict
            pass

        # If it's not a BaseModel and not a Sequence,
        # it might be a generator or custom object
        # Try directly:
        try:
            return dict(input_)
        except TypeError:
            # Not directly dict-able
            # If it's iterable but not a sequence, handle as iterable:
            if isinstance(input_, Iterable) and not isinstance(
                input_, Sequence
            ):
                return _iterable_to_dict(input_)
            raise ValueError("Unable to convert input to dictionary")


def _set_to_dict(input_: set, /) -> dict[str, Any]:
    return {str(v): v for v in input_}


def _iterable_to_dict(input_: Iterable, /) -> dict[str, Any]:
    return {str(idx): v for idx, v in enumerate(input_)}


def _to_dict(
    input_: Any,
    /,
    *,
    fuzzy_parse: bool,
    str_type: Literal["json", "xml"] | None,
    parser: Callable[[str], Any] | None,
    use_model_dump: bool,
    use_enum_values: bool,
    remove_root: bool,
    root_tag: str,
) -> dict[str, Any]:

    if isinstance(input_, set):
        return _set_to_dict(input_)

    if isinstance(input_, type) and issubclass(input_, Enum):
        return _enum_to_dict(input_, use_enum_values=use_enum_values)

    if isinstance(input_, Mapping):
        return dict(input_)

    if input_ is PydanticUndefinedType:
        return {}

    if isinstance(input_, (type(None), UndefinedType, PydanticUndefinedType)):
        return _na_to_dict(input_)

    if isinstance(input_, str):
        return _str_to_dict(
            input_,
            fuzzy_parse=fuzzy_parse,
            str_type=str_type,
            parser=parser,
            remove_root=remove_root,
            root_tag=root_tag,
        )

    if isinstance(input_, BaseModel):
        return _model_to_dict(input_, use_model_dump=use_model_dump)

    # If not BaseModel and not a str
    if isinstance(input_, Sequence) and not isinstance(input_, str):
        # Sequence like list/tuple handled already
        # If we get here, it's likely a custom object not handled before
        # We do last fallback:
        try:
            return dict(input_)
        except Exception:
            # If fails, it's not a dict-convertible sequence, treat as iterable:
            return _iterable_to_dict(input_)

    if isinstance(input_, Iterable):
        return _iterable_to_dict(input_)

    # last fallback
    try:
        return dict(input_)
    except Exception as e:
        raise ValueError(f"Unable to convert input to dictionary: {e}")
