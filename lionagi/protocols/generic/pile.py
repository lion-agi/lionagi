# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import AsyncIterator, Callable, Generator, Iterator
from functools import wraps
from typing import Any, Generic, Literal, Self, TypeVar

import pandas as pd
from pydantic import Field, field_serializer, model_validator
from pydantic.fields import FieldInfo

from lionagi._errors import IDError, ItemExistsError, ItemNotFoundError
from lionagi.utils import UNDEFINED, lcall, to_list

from ._id import ID, Collective, validate_order
from .element import E, Element, IDType
from .progression import Progression

D = TypeVar("D")


def validate_collection_item_type(
    collections: Any, item_type: type = None, strict_type: bool = None
) -> dict[IDType, Element]:
    """Validate and convert collections into a dictionary of Elements.

    Args:
        collections (Any):
            Items to validate and convert.
        item_type (type, optional):
            Expected type of items if any.
        strict_type (bool, optional):
            Whether to enforce exact type matching if `item_type` is provided.

    Returns:
        dict[IDType, Element]:
            A dictionary mapping IDs to validated Elements.

    Raises:
        TypeError: If items do not meet type requirements.
        ValueError: If items are not valid Elements.
    """
    collections = to_list(
        collections, flatten=True, dropna=True, use_values=True
    )

    if item_type is not None:
        if strict_type:
            if any(type(i) not in {item_type} for i in collections):
                raise TypeError(
                    f"All items must be exactly of type {item_type}."
                )
        else:
            if any(not isinstance(item, item_type) for item in collections):
                raise TypeError(f"All items must be instances of {item_type}.")

    out = {}
    for i in collections:
        if isinstance(i, Element):
            out[i.id] = i
        else:
            raise ValueError("All items must be Element instances.")
    return out


def synchronized(func: Callable):
    """Decorator for thread-safe synchronous methods."""

    @wraps(func)
    def wrapper(self: Pile, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)

    return wrapper


def async_synchronized(func: Callable):
    """Decorator for thread-safe asynchronous methods."""

    @wraps(func)
    async def wrapper(self: Pile, *args, **kwargs):
        async with self.async_lock:
            return await func(self, *args, **kwargs)

    return wrapper


class Pile(Element, Collective, Generic[E]):
    """A thread-safe collection of Elements with ordered progression.

    This class manages a collection of Elements with support for synchronous
    and asynchronous operations, type validation, and ordered progression
    tracking.

    Attributes:
        collections (dict[IDType, E]):
            A dictionary mapping IDs to Elements.
        item_type (type | None):
            An optional type constraint for stored items.
        strict_type (bool):
            Whether to enforce exact type matching.
        progression (Progression):
            A Progression instance tracking the order of items in the
            collection.

    Examples:
        >>> pile = Pile(collections=[element1, element2])
        >>> pile.append(element3)
        >>> async with pile:
        ...     await pile.aset(0, element4)
    """

    collections: dict[IDType, E] = Field(default_factory=dict)
    item_type: type | None = Field(default=None, frozen=True)
    strict_type: bool = Field(default=False, frozen=True)
    progression: Progression = Field(default_factory=Progression)

    def __pydantic_extra__(self) -> dict[str, FieldInfo]:
        """Define custom fields (_lock, _async_lock) for thread-safety."""
        return {
            "_lock": Field(default_factory=threading.Lock),
            "_async_lock": Field(default_factory=asyncio.Lock),
        }

    def __pydantic_private__(self) -> dict[str, FieldInfo]:
        """Define private fields for internal usage."""
        return self.__pydantic_extra__()

    @property
    def name(self) -> str:
        """str: Name of the progression."""
        return self.progression.name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the progression."""
        self.progression.name = value

    @model_validator(mode="before")
    def _validate_item_type(cls, values: dict) -> dict:
        """Validate item types and ensure progression consistency.

        Args:
            values (dict):
                A dictionary of field values before model instantiation.

        Returns:
            dict: The updated dictionary of field values.

        Raises:
            ValueError: If `item_type` or `strict_type` has invalid types, or
                if collections do not match the progression order.
        """
        params = {}
        if "item_type" in values:
            if not isinstance(values["item_type"], type):
                raise ValueError("item_type must be a type.")
            params["item_type"] = values["item_type"]

        if "strict_type" in values:
            if not isinstance(values["strict_type"], bool):
                raise ValueError("strict_type must be a boolean.")
            params["strict_type"] = values["strict_type"]

        if "collections" in values:
            try:
                params["collections"] = validate_collection_item_type(
                    values["collections"], **params
                )
            except Exception as e:
                msg = f"Invalid collection items: {e}"
                raise ValueError(msg) from e

        if "progression" not in values:
            # If no progression is given, create one from collection keys
            # if collections present.
            if "collections" in params:
                params["progression"] = Progression(
                    order=list(params["collections"].keys())
                )
            return params

        progression = values["progression"]
        if isinstance(progression, Progression):
            progression = progression.order

        params["progression"] = Progression(order=progression)

        # Ensure collections and progression have the same items
        if "progression" in params:
            coll_ids = set(params.get("collections", {}).keys())
            prog_ids = set(params["progression"].order)
            if coll_ids != prog_ids:
                raise ValueError(
                    "Collections and progression must have the same items."
                )
        return params

    @field_serializer("collections")
    def _serialize_collections(
        self, collections: dict[IDType, E]
    ) -> dict[str, dict]:
        """Serialize the collections by converting keys to strings."""
        return {str(k): v.to_dict() for k, v in collections.items()}

    @field_serializer("progression")
    def _serialize_progression(self, progression: Progression) -> list[str]:
        """Serialize the progression order."""
        return [str(item) for item in progression.order]

    def __contains__(self, item: ID.RefSeq) -> bool:
        """Check if item(s) exist in the collection.

        Args:
            item (ID.RefSeq):
                A reference to one or more items.

        Returns:
            bool: True if all items exist, False otherwise.
        """
        get_id = ID.get_id
        items = to_list(item, flatten=True, dropna=True, use_values=True)
        for i in items:
            try:
                item_id = get_id(i)
                if item_id not in self.collections:
                    return False
            except Exception:
                return False
        return True

    def __setitem__(self, key: ID.RefSeq | int | slice, value: ID.ItemSeq):
        """Set item(s) at the specified key or index.

        Args:
            key (ID.RefSeq | int | slice):
                A reference or index specifying where to set items.
            value (ID.ItemSeq):
                The items to set.

        Raises:
            IndexError: If the integer index is out of range.
            ItemExistsError: If an item already exists in the Pile.
            KeyError: If key references do not match value IDs.
        """
        item_dict = validate_collection_item_type(
            value, self.item_type, self.strict_type
        )
        new_ids = list(item_dict.keys())

        if isinstance(key, int):
            # Convert negative index
            if key < 0:
                key = len(self.progression) + key
            if key < 0 or key > len(self.progression):
                raise IndexError("Index out of range.")

            if key == len(self.progression):
                self.progression.insert(key, new_ids)
                self.collections.update(item_dict)
            else:
                delete_order = self.progression[key]
                if any(i in self.collections for i in new_ids):
                    for i in new_ids:
                        if i in self.collections and i not in to_list(
                            delete_order, flatten=True
                        ):
                            raise ItemExistsError(
                                "Item already exists in the pile."
                            )
                self.progression[key] = new_ids
                for old_id in to_list(delete_order, flatten=True):
                    self.collections.pop(old_id, None)
                self.collections.update(item_dict)

        elif isinstance(key, slice):
            slice_items = self.progression[key]
            for i in new_ids:
                if i in self.collections and i not in to_list(
                    slice_items, flatten=True
                ):
                    raise ItemExistsError("Item already exists in the pile.")
            self.progression[key] = new_ids
            for old_id in to_list(slice_items, flatten=True):
                self.collections.pop(old_id, None)
            self.collections.update(item_dict)

        else:
            processed_key = lcall(
                key,
                ID.get_id,
                sanitize_input=True,
                flatten=True,
                dropna=True,
                unique_output=True,
            )
            if len(processed_key) != len(item_dict) or any(
                i not in item_dict for i in processed_key
            ):
                raise KeyError(
                    f"Invalid key {processed_key}. "
                    "Key and item do not match."
                )

            for i in new_ids:
                if i not in processed_key and i in self.collections:
                    raise ItemExistsError("Item already exists in the pile.")

            self.progression.include(processed_key)
            self.collections.update(item_dict)

    @synchronized
    def set(self, key: ID.RefSeq | int | slice, value: ID.ItemSeq) -> None:
        """Thread-safe set operation."""
        self[key] = value

    @async_synchronized
    async def aset(
        self, key: ID.RefSeq | int | slice, value: ID.ItemSeq
    ) -> None:
        """Async thread-safe set operation."""
        self[key] = value

    def __getitem__(self, key: ID.RefSeq | int | slice) -> ID.ItemSeq:
        """Get item(s) by key or index.

        Args:
            key (ID.RefSeq | int | slice):
                The key, integer index, or slice specifying the item(s).

        Returns:
            ID.ItemSeq: The retrieved item(s).

        Raises:
            ItemNotFoundError: If an item is not found.
        """
        try:
            if isinstance(key, (int, slice)):
                result_ids = self.progression[key]
                if not isinstance(result_ids, list):
                    result_ids = [result_ids]
                if len(result_ids) == 1:
                    return self.collections[result_ids[0]]
                return [self.collections[i] for i in result_ids]

            # Convert key to IDs if not int or slice
            out_ids = []
            try:
                out_ids = lcall(
                    key,
                    ID.get_id,
                    sanitize_input=True,
                    flatten=True,
                    dropna=True,
                    unique_output=True,
                )
            except IDError:
                raise ItemNotFoundError(
                    f"Item with id {key} not found in the pile."
                )

            out_items = []
            for oid in out_ids:
                if oid not in self.collections:
                    raise ItemNotFoundError(
                        f"Item with id {oid} not found in the pile."
                    )
                out_items.append(self.collections[oid])
            return out_items[0] if len(out_items) == 1 else out_items
        except (KeyError, IndexError):
            raise ItemNotFoundError(
                f"Item with id {key} not found in the pile."
            )

    def _get(
        self, key: ID.RefSeq | int | slice, default: D = UNDEFINED
    ) -> E | D | list[E]:
        """Internal get with default value handling.

        Args:
            key (ID.RefSeq | int | slice):
                The key, index, or slice specifying the item(s).
            default (D):
                Default value if the item is not found.

        Returns:
            E | D | list[E]:
                The item(s) or the default value if not found.

        Raises:
            ItemNotFoundError: If not found and `default` is UNDEFINED.
        """
        try:
            return self[key]
        except ItemNotFoundError:
            if default is not UNDEFINED:
                return default
            raise

    @synchronized
    def get(
        self, key: ID.RefSeq | int | slice, default: D = UNDEFINED
    ) -> E | D | list[E]:
        """Thread-safe get operation with default value."""
        return self._get(key, default)

    @async_synchronized
    async def aget(
        self, key: ID.RefSeq | int | slice, default: D = UNDEFINED
    ) -> E | D | list[E]:
        """Async thread-safe get operation with default value."""
        return self._get(key, default)

    def include(self, item: ID.ItemSeq) -> bool:
        """Include items without raising errors.

        Args:
            item (ID.ItemSeq):
                The item or items to be included.

        Returns:
            bool: True if items were included or already present; False if
            they failed validation.
        """
        try:
            item_dict = validate_collection_item_type(
                item, self.item_type, self.strict_type
            )
        except Exception:
            return False

        if not item_dict:
            return True
        self.progression.include(list(item_dict.keys()))
        self.collections.update(item_dict)
        return True

    @async_synchronized
    async def ainclude(self, item: ID.ItemSeq) -> bool:
        """Async thread-safe include operation."""
        return self.include(item)

    def _append(self, item: ID.ItemSeq) -> None:
        """Append items to the pile.

        Raises:
            ItemExistsError: If an item already exists in the pile.
            ValueError: If item is not a valid Element.
        """
        item_dict = validate_collection_item_type(
            item, self.item_type, self.strict_type
        )
        if any(i in self.collections for i in item_dict):
            raise ItemExistsError("Item already exists in the pile.")
        self.progression.append(list(item_dict.keys()))
        self.collections.update(item_dict)

    @synchronized
    def append(self, item: ID.ItemSeq) -> None:
        """Thread-safe append operation."""
        self._append(item)

    def exclude(self, item: ID.RefSeq) -> bool:
        """Exclude items without raising errors.

        Args:
            item (ID.RefSeq):
                A reference (ID, list of IDs, or Element) specifying
                the items to exclude.

        Returns:
            bool: True if items were excluded or not found; False if
            validation fails.
        """
        try:
            item_ids = validate_order(item)
        except ValueError:
            return False
        if not item_ids:
            return True

        for i in item_ids:
            if i in self.collections:
                self.collections.pop(i, None)
                self.progression.exclude(i)
        return True

    @async_synchronized
    async def aexclude(self, item: ID.RefSeq) -> bool:
        """Async thread-safe exclude operation."""
        return self.exclude(item)

    def _pop(self, item: ID.RefSeq, default: D = UNDEFINED) -> E | list[E] | D:
        """Internal pop implementation with a default value.

        Args:
            item (ID.RefSeq):
                A reference, index, or slice specifying the item(s).
            default (D):
                Default value if item is not found.

        Returns:
            E | list[E] | D:
                The popped item(s), or the default value if not found.

        Raises:
            ItemNotFoundError: If item is not found and `default` is UNDEFINED.
        """
        try:
            item_ids = []
            if isinstance(item, (int, slice)):
                item_ids = self.progression[item]
            else:
                item_ids = validate_order(item)
            if not isinstance(item_ids, list):
                item_ids = [item_ids]
            out = []
            for i in item_ids:
                if i not in self.collections:
                    msg = f"Item with id {i} not found in the pile."
                    raise ItemNotFoundError(msg)
                out.append(self.collections.pop(i))
                self.progression.exclude(i)
            return out[0] if len(out) == 1 else out
        except Exception as e:
            if default is not UNDEFINED:
                return default
            msg = f"Item with id {item} not found in the pile."
            raise ItemNotFoundError(msg) from e

    @synchronized
    def popleft(self) -> E:
        """Pop the first item in the progression.

        Returns:
            E: The popped item.

        Raises:
            ItemNotFoundError: If the pile is empty.
        """
        return self._pop(self.progression.popleft())

    @async_synchronized
    async def apopleft(self) -> E:
        """Async pop of the first item in the progression."""
        return self._pop(self.progression.popleft())

    @synchronized
    def pop(
        self, item: ID.RefSeq = 0, default: D = UNDEFINED
    ) -> E | list[E] | D:
        """Thread-safe pop operation.

        Args:
            item (ID.RefSeq, optional):
                A reference, index, or slice specifying the item(s) to pop.
                Defaults to 0 (the first item).
            default (D):
                Default value if the item(s) is not found.

        Returns:
            E | list[E] | D: The popped item(s), or the default value.
        """
        return self._pop(item, default)

    @async_synchronized
    async def apop(
        self, item: ID.RefSeq = 0, default: D = UNDEFINED
    ) -> E | list[E] | D:
        """Async thread-safe pop operation."""
        return self._pop(item, default)

    def __getstate__(self) -> dict[str, Any]:
        """Get the object's state for pickling."""
        state = self.__dict__.copy()
        state["_lock"] = None
        state["_async_lock"] = None
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore the object's state after unpickling."""
        self.__dict__.update(state)
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    @property
    def lock(self) -> threading.Lock:
        """threading.Lock: Thread lock for synchronization."""
        if not hasattr(self, "_lock") or self._lock is None:
            self._lock = threading.Lock()
        return self._lock

    @property
    def async_lock(self) -> asyncio.Lock:
        """asyncio.Lock: Async lock for synchronization."""
        if not hasattr(self, "_async_lock") or self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    def __iter__(self) -> Iterator[E]:
        """Iterate over the items in the pile in order.

        Returns:
            Iterator[E]: An iterator over the elements.
        """
        with self.lock:
            current_order = list(self.progression)
        for key in current_order:
            yield self.collections[key]

    def keys(self) -> Generator[IDType, None, None]:
        """Get the ordered list of collection keys."""
        return (i for i in self.progression.order[:])

    def values(self) -> Generator[E, None, None]:
        """Get the ordered list of collection values."""
        return (self.collections[i] for i in list(self.progression))

    def items(self) -> Generator[tuple[IDType, E], None, None]:
        """Get collection items as (key, value) pairs."""
        return ((i, self.collections[i]) for i in self.progression)

    @synchronized
    def insert(self, index: int, item: ID.Item) -> None:
        """Insert item(s) at the specified index without replacement.

        Args:
            index (int):
                The position at which to insert items.
            item (ID.Item):
                The item(s) to insert.

        Raises:
            ItemExistsError: If the item(s) already exists in the pile.
        """
        item_dict = validate_collection_item_type(
            item, self.item_type, self.strict_type
        )
        for i in item_dict:
            if i in self.progression:
                msg = f"item {i} already exists in the pile"
                raise ItemExistsError(msg)
        self.progression.insert(index, list(item_dict.keys()))
        self.collections.update(item_dict)

    def _clear(self) -> None:
        """Internal clear operation for removing all items."""
        self.collections.clear()
        self.progression.clear()

    @synchronized
    def clear(self) -> None:
        """Remove all items from the collection."""
        self._clear()

    @async_synchronized
    async def aclear(self) -> None:
        """Async operation to remove all items from the collection."""
        self._clear()

    def _update(self, other: ID.ItemSeq | ID.Item) -> None:
        """Internal update operation.

        Updates existing items or includes new ones. Items must be valid
        Elements.

        Args:
            other (ID.ItemSeq | ID.Item):
                An item or sequence of items to update/include.

        Raises:
            ValueError: If an item is not an Element.
        """
        items = to_list(other, flatten=True, dropna=True, use_values=True)
        if any(not isinstance(x, Element) for x in items):
            raise ValueError("All items must be Element instances.")
        others = {x.id: x for x in items}
        for i, val in others.items():
            if i in self.collections:
                self.collections[i] = val
            else:
                self.include(val)

    def update(self, other: ID.ItemSeq | ID.Item) -> None:
        """Update existing items or include new ones."""
        self._update(other)

    @async_synchronized
    async def aupdate(self, other: ID.ItemSeq | ID.Item) -> None:
        """Async operation to update existing items or include new ones."""
        self._update(other)

    async def __aiter__(self) -> AsyncIterator[E]:
        """Async iterate over items.

        Yields:
            E: Each item in the pile.
        """
        async with self.async_lock:
            current_order = list(self.progression)

        for key in current_order:
            yield self.collections[key]
            await asyncio.sleep(0)  # Yield control to the event loop

    @async_synchronized
    async def asetitem(
        self,
        key: ID.Ref | ID.RefSeq | int | slice,
        item: ID.Item | ID.ItemSeq,
        /,
    ) -> None:
        """Async set item(s)."""
        self.set(key, item)

    class AsyncPileIterator:
        """An async iterator for the Pile."""

        def __init__(self, pile: Pile):
            self.pile = pile
            self.index = 0

        def __aiter__(self) -> AsyncIterator[E]:
            return self

        async def __anext__(self) -> E:
            if self.index >= len(self.pile):
                raise StopAsyncIteration
            item_id = self.pile.progression[self.index]
            item = self.pile.collections[item_id]
            self.index += 1
            await asyncio.sleep(0)
            return item

    async def __aenter__(self) -> Self:
        """Enter the async context manager."""
        await self.async_lock.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit the async context manager."""
        self.async_lock.release()

    def __len__(self) -> int:
        """int: The number of items in the pile."""
        return len(self.collections)

    def __list__(self) -> list[E]:
        """Convert the pile to a list of its values."""
        return list(self.values())

    def __or__(self, other: Pile) -> Pile:
        """Create a new Pile with the union of items from both piles.

        Args:
            other (Pile): The pile to union with.

        Returns:
            Pile: A new pile containing all items from both piles.

        Raises:
            ValueError: If `other` is not a Pile or items don't match
                `item_type`.
        """
        if not isinstance(other, Pile):
            raise ValueError("Only Pile instances can be unioned.")
        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            msg = "All items must be exactly of type {self.item_type}."
            raise ValueError(msg)
        result = self.__class__(
            collections=self.collections,
            item_type=self.item_type,
            strict_type=self.strict_type,
            progression=self.progression,
        )
        result._update(other)
        return result

    def __ior__(self, other: Pile) -> Self:
        """In-place union with items from `other`.

        Args:
            other (Pile): The pile to union with.

        Returns:
            Self: The updated pile.

        Raises:
            ValueError: If `other` is not a Pile or items don't match
                `item_type`.
        """
        if not isinstance(other, Pile):
            raise ValueError("Only Pile instances can be unioned.")
        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            msg = "All items must be exactly of type {self.item_type}."
            raise ValueError(msg)
        other = validate_collection_item_type(
            other, self.item_type, self.strict_type
        )
        self._update(other)
        return self

    def __xor__(self, other: Pile) -> Pile:
        """Create a new Pile with the symmetric difference of the two piles.

        Args:
            other (Pile): The pile to compute symmetric difference with.

        Returns:
            Pile: A new pile containing items present in either pile but not both.

        Raises:
            ValueError: If `other` is not a Pile or items don't match `item_type`.
        """
        if not isinstance(other, Pile):
            raise ValueError(
                "Only Pile instances can be symmetric differenced."
            )
        if self.item_type:
            _ = validate_collection_item_type(
                list(other), self.item_type, self.strict_type
            )
            raise ValueError(
                "All items must be exactly of type {self.item_type}."
            )

        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        values = [i for i in self if i not in to_exclude]
        values += [i for i in other if i not in to_exclude]

        result = self.__class__(
            collections=values,
            item_type=self.item_type,
            strict_type=self.strict_type,
        )
        return result

    def __ixor__(self, other: Pile) -> Self:
        """In-place symmetric difference of the two piles.

        Args:
            other (Pile): The pile to compute symmetric difference with.

        Returns:
            Self: The updated pile containing items present in either pile but
            not both.

        Raises:
            ValueError: If `other` is not a Pile or items don't match `item_type`.
        """
        if not isinstance(other, Pile):
            raise ValueError(
                "Only Pile instances can be symmetric differenced."
            )
        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            msg = "All items must be exactly of type {self.item_type}."
            raise ValueError(msg)

        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        other_remaining = [i for i in other if i not in to_exclude]
        self.exclude(to_exclude)
        self.include(other_remaining)
        return self

    def __iand__(self, other: Pile) -> Self:
        """In-place intersection with another pile.

        Keeps only items present in both piles.

        Args:
            other (Pile): The pile to intersect with.

        Returns:
            Self: The updated pile with the intersection result.

        Raises:
            ValueError: If `other` is not a Pile or items don't match `item_type`.
        """
        if not isinstance(other, Pile):
            raise ValueError(
                "Only Pile instances can be symmetric differenced."
            )
        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            msg = "All items must be exactly of type {self.item_type}."
            raise ValueError(msg)

        to_exclude = []
        for i in self.values():
            if i not in other:
                to_exclude.append(i)
        self.exclude(to_exclude)
        return self

    def __and__(self, other: Pile) -> Pile:
        """Create a new Pile with items common to both piles (intersection).

        Args:
            other (Pile): The pile to intersect with.

        Returns:
            Pile: A new pile containing items present in both piles.

        Raises:
            ValueError: If `other` is not a Pile or items don't match `item_type`.
        """
        if not isinstance(other, Pile):
            raise ValueError(
                "Only Pile instances can be symmetric differenced."
            )
        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            msg = "All items must be exactly of type {self.item_type}."
            raise ValueError(msg)

        values = [i for i in self if i in other]
        return self.__class__(
            collections=values,
            item_type=self.item_type,
            strict_type=self.strict_type,
        )

    def to_df(
        self,
        *,
        index=...,
        exclude=...,
        columns=...,
        coerce_float=...,
        nrows=...,
        **kwargs,
    ) -> pd.DataFrame:
        """Convert the pile to a pandas DataFrame.

        Args:
            index:
                (Optional) Passed to `pd.DataFrame.from_records()`.
            exclude:
                (Optional) Passed to `pd.DataFrame.from_records()`.
            columns:
                (Optional) Passed to `pd.DataFrame.from_records()`.
            coerce_float:
                (Optional) Passed to `pd.DataFrame.from_records()`.
            nrows:
                (Optional) Passed to `pd.DataFrame.from_records()`.
            **kwargs:
                Additional keyword arguments passed to each element's
                `to_dict()` method (if supported by that element).

        Returns:
            pd.DataFrame: A DataFrame representation of the pile's items.
        """
        dicts_ = [i.to_dict(**kwargs) for i in self.values()]
        params = {
            "index": index,
            "exclude": exclude,
            "columns": columns,
            "coerce_float": coerce_float,
            "nrows": nrows,
        }
        clean_params = {k: v for k, v in params.items() if v is not ...}
        return pd.DataFrame.from_records(dicts_, **clean_params)

    def to_csv(
        self,
        path_or_buf,
        /,
        *,
        verbose=False,
        sep=...,
        na_rep=...,
        float_format=...,
        columns=...,
        header=...,
        index: bool = ...,
        index_label: str | list | Literal[False] | None = ...,
        mode=...,
        encoding: str | None = ...,
        compression=...,
        quoting=...,
        quotechar: str = ...,
        lineterminator: str | None = ...,
        chunksize: int | None = ...,
        date_format: str | None = ...,
        doublequote: bool = ...,
        escapechar: str | None = ...,
        decimal: str = ...,
        errors: str = ...,
        storage_options=...,
    ) -> None:
        """Export the collection to a CSV file.

        Args:
            path_or_buf:
                File path or buffer to which the CSV is written.
            verbose (bool, optional):
                Whether to print a confirmation message.
            Other parameters are forwarded to `pandas.DataFrame.to_csv()`.
        """
        params = {k: v for k, v in locals().items() if v is not ...}
        params.pop("self")
        params.pop("verbose")

        self.to_df().to_csv(**params)
        if verbose:
            print(f"Saved Pile to {path_or_buf}")

    def to_json(
        self,
        path_or_buf,
        *,
        use_pd: bool = False,
        mode="w",
        verbose=False,
        **kwargs,
    ) -> None:
        """Export the collection to a JSON file.

        Args:
            path_or_buf:
                File path or buffer to which the JSON is written.
            use_pd (bool, optional):
                Use pandas JSON export if True. Otherwise, use `json.dump`.
            mode (str, optional):
                File open mode. Defaults to "w".
            verbose (bool, optional):
                Whether to print a confirmation message.
            **kwargs:
                Additional arguments for `pd.DataFrame.to_json` or `json.dump`.
        """
        if use_pd:
            return self.to_df().to_json(mode=mode, **kwargs)
        dict_ = self.to_dict()
        with open(path_or_buf, mode) as f:
            json.dump(dict_, f, **kwargs)

        if verbose:
            print(f"Saved Pile to {path_or_buf}")

    def dump(
        self,
        path_or_buf,
        *,
        file_type: Literal["json", "csv"] = "json",
        clear: bool = False,
        verbose: bool = False,
        **kwargs,
    ) -> None:
        """Export the collection to a file and optionally clear it.

        Args:
            path_or_buf:
                File path or buffer to write to.
            file_type (Literal["json", "csv"], optional):
                Format to export as. Defaults to "json".
            clear (bool, optional):
                Whether to clear the collection after export.
            verbose (bool, optional):
                Whether to print a confirmation message.
            **kwargs:
                Additional arguments for JSON or CSV export.
                - For JSON: `use_pd` (bool), `mode` (str),
                  plus JSON-specific kwargs.
                - For CSV: see `pandas.DataFrame.to_csv`.
        """
        match file_type:
            case "json":
                self.to_json(path_or_buf, **kwargs)
            case "csv":
                self.to_csv(path_or_buf, **kwargs)

        if clear:
            self._clear()

        if verbose:
            print(f"Saved Pile to {path_or_buf}")

    @async_synchronized
    async def adump(
        self,
        path_or_buf,
        *,
        file_type: Literal["json", "csv"] = "json",
        clear: bool = False,
        verbose: bool = False,
        **kwargs,
    ) -> None:
        """Async operation to dump the collection to a file."""
        self.dump(
            path_or_buf,
            file_type=file_type,
            clear=clear,
            verbose=verbose,
            **kwargs,
        )

    @classmethod
    def create(
        cls,
        collections: ID.ItemSeq,
        item_type: type = None,
        strict_type: bool = False,
        progression: Progression | ID.RefSeq = None,
    ) -> Self:
        """Create a new Pile instance.

        Args:
            collections (ID.ItemSeq):
                The initial items for the Pile.
            item_type (type, optional):
                A type constraint for the items.
            strict_type (bool, optional):
                Whether to enforce exact type matching.
            progression (Progression | ID.RefSeq, optional):
                A custom item ordering.

        Returns:
            Pile: A new Pile instance.
        """
        params = {}
        if item_type is not None:
            params["item_type"] = item_type
        if strict_type is not False:
            params["strict_type"] = strict_type
        if progression is not None:
            params["progression"] = progression
        if collections:
            params["collections"] = collections

        return cls(**params)

    def __next__(self) -> E:
        """Get the next item in iteration.

        Returns:
            E: The next item.

        Raises:
            StopIteration: If no more items are in the pile.
        """
        try:
            return next(iter(self))
        except StopIteration:
            raise StopIteration("End of pile")

    def __str__(self) -> str:
        """str: A string representation of the pile as a DataFrame."""
        return str(self.to_df())

    def __repr__(self) -> str:
        """str: Detailed string representation of the pile."""
        length = len(self)
        if length == 0:
            return "Pile()"
        if length == 1:
            single_val = next(iter(self.collections.values()))
            return f"Pile({single_val.__repr__()})"
        return repr(self.to_df())

    def __bool__(self) -> bool:
        """bool: True if the pile has any items, False otherwise."""
        return bool(self.collections)


def pile(
    collections: ID.ItemSeq,
    item_type: type = None,
    strict_type: bool = False,
    progression: Progression | ID.RefSeq = None,
) -> Pile:
    """Convenience function to create a new Pile instance.

    Args:
        collections (ID.ItemSeq):
            The initial items for the Pile.
        item_type (type, optional):
            A type constraint for the items.
        strict_type (bool, optional):
            Whether to enforce exact type matching.
        progression (Progression | ID.RefSeq, optional):
            A custom item ordering.

    Returns:
        Pile: A new Pile instance.
    """
    return Pile.create(
        collections,
        item_type=item_type,
        strict_type=strict_type,
        progression=progression,
    )
