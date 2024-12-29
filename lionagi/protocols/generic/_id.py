# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import uuid
from collections.abc import Mapping, Sequence
from typing import Any, Generic, TypeAlias

from lionagi._errors import IDError

from .concepts import Collective, Ordering
from .element import E, Element, IDType

__all__ = (
    "validate_order",
    "ID",
    "IDType",
    "IDError",
)


def validate_order(order: Any) -> list[IDType]:
    """Validate and normalize ordering specs into a list of UUID4s."""
    # If it's a single Element
    if isinstance(order, Element):
        return [order.id]

    # if mapping, we assume key is id type
    if isinstance(order, Mapping):
        order = list(order.keys())

    # Flatten the input, skipping None and extracting UUIDs from Elements
    stack = [order]
    flattened = []
    while stack:
        current = stack.pop()
        if current is None:
            continue
        if isinstance(current, Element):
            flattened.append(current.id)
        elif isinstance(current, IDType):
            flattened.append(current)
        elif isinstance(current, uuid.UUID):
            flattened.append(str(current))
        elif isinstance(current, str):
            flattened.append(current)
        elif isinstance(current, (list, tuple, set)):
            # Reverse extend to maintain order
            stack.extend(reversed(current))
        else:
            # If we encounter an invalid type, fail early
            raise ValueError(
                "All items must be of type str, Element, or IDType."
            )

    # If empty after flattening
    if not flattened:
        return []

    # Determine the data type from the first element
    first_type = type(flattened[0])
    if first_type is str:
        # Ensure all are strings before converting
        if any(not isinstance(item, str) for item in flattened):
            raise ValueError(
                "All items must be of a single, consistent type (str, Element, or IDType)."
            )
        # Convert all to UUID4
        return [IDType(uuid.UUID(item, version=4)) for item in flattened]
    elif first_type is IDType:
        # Ensure all are UUID4
        if any(not isinstance(item, IDType) for item in flattened):
            raise ValueError(
                "All items must be of a single, consistent type (str, Element, or IDType)."
            )
        return flattened
    else:
        raise ValueError("All items must be of type str, Element, or IDType.")


class ID(Generic[E]):

    ID: TypeAlias = IDType
    Item: TypeAlias = E | Element  # type: ignore
    Ref: TypeAlias = IDType | E | str  # type: ignore
    ItemSeq: TypeAlias = Sequence[E] | Collective[E]  # type: ignore
    RefSeq: TypeAlias = ItemSeq | Sequence[Ref] | Ordering[E]  # type: ignore

    @staticmethod
    def get_id(item: E, /) -> IDType:
        if isinstance(item, Element):
            return item.id
        if isinstance(item, IDType | str | uuid.UUID):
            return IDType.validate(item)
        raise ValueError(
            "Item must be of type Element, str, a valid UUID4 or IDtype."
        )

    @staticmethod
    def is_id(item: Any, /) -> bool:
        try:
            return IDType.validate(item)
        except Exception:
            return False
