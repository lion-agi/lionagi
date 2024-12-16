# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections import deque
from collections.abc import Generator
from typing import Any, TypeVar

from lionagi.core.typing import ID, IDError

from .element import Element

T = TypeVar("T")


def to_list_type(value: Any, /) -> list[Any]:
    """Convert input to a list format"""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if ID.is_id(value) else []
    if isinstance(value, Element):
        return [value]
    if hasattr(value, "values") and callable(value.values):
        return list(value.values())
    if isinstance(value, list | tuple | set | deque | Generator):
        return list(value)
    return [value]


def validate_order(value: Any, /) -> list[str]:
    """Validate and standardize order representation"""

    try:
        result = []
        for item in to_list_type(value):
            if isinstance(item, str) and ID.is_id(item):
                result.append(item)
            elif isinstance(item, Element):
                result.append(item.ln_id)
            else:
                id_ = ID.get_id(item)
                if id_:
                    result.append(id_)
        return result
    except Exception as e:
        raise IDError("Must only contain valid Lion IDs.") from e


# File: autoos/container/util.py
