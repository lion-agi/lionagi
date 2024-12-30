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
    """Validate and normalize ordering specifications into a list of UUID4 IDs.

    This function accepts different types of inputs (e.g., an Element, a mapping,
    a sequence, or nested structures of these) and flattens them into a list of
    IDType objects (UUID4-based). It discards `None`, extracts the `id` attribute
    from Elements, and ensures all items are valid UUID4 strings or IDTypes.

    Args:
        order (Any):
            The ordering specification to validate. It can be:
            - A single Element
            - A mapping where keys are valid UUID4 strings or IDTypes
            - A sequence (list, tuple, set) of Elements, strings, or IDTypes
            - Nested structures of the above

    Returns:
        list[IDType]:
            A list of validated IDType objects (UUID4-based).

    Raises:
        ValueError: If any item in `order` is not a valid type or if the types
            are inconsistent.
    """
    if isinstance(order, Element):
        return [order.id]

    if isinstance(order, Mapping):
        order = list(order.keys())

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
            stack.extend(reversed(current))
        else:
            raise ValueError(
                "All items must be of type str, Element, or IDType."
            )

    if not flattened:
        return []

    first_type = type(flattened[0])
    if first_type is str:
        if any(not isinstance(item, str) for item in flattened):
            raise ValueError(
                "All items must be of a single, consistent type "
                "(str, Element, or IDType)."
            )
        return [IDType(uuid.UUID(item, version=4)) for item in flattened]

    if first_type is IDType:
        if any(not isinstance(item, IDType) for item in flattened):
            raise ValueError(
                "All items must be of a single, consistent type "
                "(str, Element, or IDType)."
            )
        return flattened

    raise ValueError("All items must be of type str, Element, or IDType.")


class ID(Generic[E]):
    """Utility class for working with IDType in a generic way.

    This class provides static methods to retrieve and validate the ID
    attribute from objects of type Element or other compatible types.
    """

    ID: TypeAlias = IDType
    Item: TypeAlias = E | Element  # type: ignore
    Ref: TypeAlias = IDType | E | str  # type: ignore
    ItemSeq: TypeAlias = Sequence[E] | Collective[E]  # type: ignore
    RefSeq: TypeAlias = ItemSeq | Sequence[Ref] | Ordering[E]  # type: ignore

    @staticmethod
    def get_id(item: E, /) -> IDType:
        """Retrieve a valid IDType from an item.

        If `item` is an Element, its `id` attribute is returned. If `item` is
        a string, a UUID, or already an IDType, it is validated or converted
        into a valid IDType object.

        Args:
            item (E):
                The item from which to retrieve an ID. Could be an Element, a UUID,
                an IDType, or a string representing a valid UUID4.

        Returns:
            IDType:
                A valid IDType object (UUID4-based).

        Raises:
            ValueError: If `item` is not a valid type (Element, str, UUID, or IDType).
        """
        if isinstance(item, Element):
            return item.id
        if isinstance(item, (IDType, str, uuid.UUID)):
            return IDType.validate(item)
        raise ValueError(
            "Item must be of type Element, str, a valid UUID4 or IDType."
        )

    @staticmethod
    def is_id(item: Any, /) -> bool:
        """Check if the provided item is a valid IDType.

        This attempts to validate the item as an IDType. If validation fails,
        it returns False.

        Args:
            item (Any):
                The item to check.

        Returns:
            bool:
                True if `item` is a valid IDType, False otherwise.
        """
        try:
            return IDType.validate(item)
        except Exception:
            return False


# File: lionagi/protocols/generic/_id.py
