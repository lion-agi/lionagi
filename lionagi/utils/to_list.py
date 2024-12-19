# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Iterable, Mapping
from enum import Enum
from typing import Any, overload

from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType

from .undefined import UndefinedType


@overload
def to_list(
    input_: None | UndefinedType | PydanticUndefinedType,
    /,
) -> list: ...


@overload
def to_list(
    input_: str | bytes | bytearray,
    /,
    use_values: bool = False,
) -> list[str | bytes | bytearray]: ...


@overload
def to_list(
    input_: Mapping,
    /,
    use_values: bool = False,
) -> list[Any]: ...


@overload
def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
    use_values: bool = False,
    flatten_tuple_set: bool = False,
) -> list: ...


def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
    use_values: bool = False,
    flatten_tuple_set: bool = False,
) -> list:
    """Convert input to a list with optional transformations.

    Transforms various input types into a list with configurable processing
    options for flattening, filtering, and value extraction.

    Args:
        input_: Value to convert to list.
        flatten: If True, recursively flatten nested iterables.
        dropna: If True, remove None and undefined values.
        unique: If True, remove duplicates (requires flatten=True).
        use_values: If True, extract values from enums/mappings.
        flatten_tuple_items: If True, include tuples in flattening.
        flatten_set_items: If True, include sets in flattening.

    Returns:
        list: Processed list based on input and specified options.

    Raises:
        ValueError: If unique=True is used without flatten=True.

    Examples:
        >>> to_list([1, [2, 3], 4], flatten=True)
        [1, 2, 3, 4]
        >>> to_list([1, None, 2], dropna=True)
        [1, 2]
    """

    def _process_list(
        lst: list[Any],
        flatten: bool,
        dropna: bool,
    ) -> list[Any]:
        """Process list according to flatten and dropna options.

        Args:
            lst: Input list to process.
            flatten: Whether to flatten nested iterables.
            dropna: Whether to remove None/undefined values.

        Returns:
            list: Processed list based on specified options.
        """
        result = []
        skip_types = (str, bytes, bytearray, Mapping, BaseModel, Enum)

        if not flatten_tuple_set:
            skip_types += (tuple, set, frozenset)

        for item in lst:
            if dropna and (
                item is None
                or isinstance(item, (UndefinedType, PydanticUndefinedType))
            ):
                continue

            is_iterable = isinstance(item, Iterable)
            should_skip = isinstance(item, skip_types)

            if is_iterable and not should_skip:
                item_list = list(item)
                if flatten:
                    result.extend(
                        _process_list(
                            item_list, flatten=flatten, dropna=dropna
                        )
                    )
                else:
                    result.append(
                        _process_list(
                            item_list, flatten=flatten, dropna=dropna
                        )
                    )
            else:
                result.append(item)

        return result

    def _to_list_type(input_: Any, use_values: bool) -> list[Any]:
        """Convert input to initial list based on type.

        Args:
            input_: Value to convert to list.
            use_values: Whether to extract values from containers.

        Returns:
            list: Initial list conversion of input.
        """
        if input_ is None or isinstance(
            input_, (UndefinedType, PydanticUndefinedType)
        ):
            return []

        if isinstance(input_, list):
            return input_

        if isinstance(input_, type) and issubclass(input_, Enum):
            members = input_.__members__.values()
            return (
                [member.value for member in members]
                if use_values
                else list(members)
            )

        if isinstance(input_, (str, bytes, bytearray)):
            return list(input_) if use_values else [input_]

        if isinstance(input_, Mapping):
            return (
                list(input_.values())
                if use_values and hasattr(input_, "values")
                else [input_]
            )

        if isinstance(input_, BaseModel):
            return [input_]

        if isinstance(input_, Iterable) and not isinstance(
            input_, (str, bytes, bytearray)
        ):
            return list(input_)

        return [input_]

    if unique and not flatten:
        raise ValueError("unique=True requires flatten=True")

    initial_list = _to_list_type(input_, use_values=use_values)
    processed = _process_list(initial_list, flatten=flatten, dropna=dropna)

    if unique:
        seen = set()
        return [x for x in processed if not (x in seen or seen.add(x))]

    return processed
