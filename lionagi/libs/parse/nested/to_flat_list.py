from collections.abc import Generator, Iterable
from typing import Any

from pydantic_core import PydanticUndefinedType

from lionagi.libs.constants import UndefinedType


def _flatten_list_generator(
    lst_: list[Any], dropna: bool
) -> Generator[Any, None, None]:
    for i in lst_:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        else:
            yield i


def to_flat_list(
    input_: Any, /, *, dropna: bool = False, unique: bool = True
) -> list[Any]:
    if isinstance(input_, type(None) | UndefinedType | PydanticUndefinedType):
        return []

    if not isinstance(input_, Iterable) or isinstance(
        input_, (str, bytes, bytearray, dict)
    ):
        return [input_]

    if isinstance(input_, list):
        return _flatten_list(input_, dropna, unique=unique)

    if isinstance(input_, tuple):
        return _flatten_list(list(input_), dropna, unique=unique)

    if isinstance(input_, set):
        return list(_dropna_iterator(list(input_))) if dropna else list(input_)

    try:
        iterable_list = list(input_)
        return _flatten_list(iterable_list, dropna, unique=unique)

    except Exception as e:
        raise ValueError(
            f"Could not convert {type(input_)} object to list: {e}"
        ) from e


def _dropna_iterator(lst_: list[Any]) -> iter:
    return (item for item in lst_ if item is not None)


def _flatten_list(
    lst_: list[Any], dropna: bool = False, unique: bool = False
) -> list[Any]:
    flattened_list = list(_flatten_list_generator(lst_, dropna))
    if dropna:
        flattened_list = list(_dropna_iterator(flattened_list))
    if unique:
        try:
            flattened_list = list(set(flattened_list))
        except Exception:
            pass
    return flattened_list
