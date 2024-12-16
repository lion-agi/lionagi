# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import uuid

from lionagi.settings import Settings

from ._concepts import (
    Container,
    Generic,
    IDType,
    ItemError,
    Observable,
    Ordering,
    T,
)
from ._typing import Container, Mapping, Sequence, TypeAlias


class IDError(ItemError):
    """Exception raised when an item does not have a Lion ID."""

    def __init__(
        self,
        message: str = "Item must contain a Lion ID.",
        item_id: str | None = None,
    ):
        super().__init__(message, item_id)


class ID(Generic[T]):
    """
    A generic class that provides ID-related functionality for Observable objects.

    This class handles the generation, validation, and management of unique identifiers
    within the Lion system. It provides type aliases for various ID-related operations
    and methods for working with IDs.
    """

    # For functions that accept either ID or item
    Ref: TypeAlias = IDType | T  # type: ignore

    # For functions requiring just the ID
    ID: TypeAlias = IDType

    # For functions requiring Observable object
    Item = T  # type: ignore

    # For collections
    IDSeq: TypeAlias = list[IDType] | Ordering
    ItemSeq: TypeAlias = (  # type: ignore
        Sequence[T] | Mapping[IDType, T] | Container[IDType | T]
    )
    RefSeq: TypeAlias = IDSeq | ItemSeq

    # For system-level interactions
    SenderRecipient: TypeAlias = IDType | T | str  # type: ignore

    @staticmethod
    def id():
        return IDType(
            _id=getattr(uuid, f"uuid{Settings.Config.UUID_VERSION}")()
        )

    @staticmethod
    def get_id(item, /) -> IDType:

        if isinstance(item, Observable):
            return item.ln_id
        try:
            return IDType.validate(item)
        except ValueError as e:
            raise IDError(
                f"The input object of type <{type(item).__name__}> does "
                "not contain or is not a valid Lion ID. Item must be an instance"
                " of `Observable` or a valid `id`."
            ) from e

    @staticmethod
    def is_id(item, /) -> bool:
        """
        Check if an item is or contains a valid Lion ID.

        Args:
            item: The item to check.
            config: Configuration dictionary for ID validation.

        Returns:
            True if the item is a valid Lion ID, False otherwise.
        """
        try:
            ID.get_id(item)
            return True
        except IDError:
            return False


__all__ = [
    "ID",
    "IDError",
]
