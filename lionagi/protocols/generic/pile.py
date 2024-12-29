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
    """Validate and convert collections to a dictionary of Elements.

    Args:
        collections: Items to validate and convert.
        item_type: Expected type of items if any.
        strict_type: Whether to enforce exact type matching.

    Returns:
        Dictionary mapping IDs to validated Elements.

    Raises:
        ValueError: If items don't meet type requirements.
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

    Manages a collection of Elements with support for synchronous and asynchronous
    operations, type validation, and ordered progression tracking.

    Attributes:
        collections: Dictionary mapping IDs to Elements.
        item_type: Optional type constraint for stored items.
        strict_type: Whether to enforce exact type matching.
        progression: Tracks order of items in collection.

    Example:
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
        return {
            "_lock": Field(default_factory=threading.Lock),
            "_async_lock": Field(default_factory=asyncio.Lock),
        }

    def __pydantic_private__(self) -> dict[str, FieldInfo]:
        return self.__pydantic_extra__()

    @property
    def name(self) -> str:
        return self.progression.name

    @name.setter
    def name(self, value: str):
        self.progression.name = value

    @model_validator(mode="before")
    def _validate_item_type(cls, values: dict) -> dict:
        """Validate item types and ensure collection-progression consistency."""
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
            # Validate collections
            try:
                params["collections"] = validate_collection_item_type(
                    values["collections"], **params
                )
            except Exception as e:
                raise ValueError(f"Invalid collection items: {e}") from e

        if "progression" not in values:
            # If no progression given, create from collections keys if collections present
            if "collections" in params:
                params["progression"] = Progression(
                    order=list(params["collections"].keys())
                )
            return params

        progression = values["progression"]
        if isinstance(progression, Progression):
            progression = progression.order

        params["progression"] = Progression(order=progression)

        # Validate collections and progression consistency
        if "progression" in params:
            if set(params.get("collections", {}).keys()) != set(
                params["progression"].order
            ):
                raise ValueError(
                    "Collections and progression must have the same items."
                )
        return params

    @field_serializer("collections")
    def _serialize_collections(
        self, collections: dict[IDType, E]
    ) -> dict[str, dict]:
        # Keys are IDType; convert to str for serialization
        return {str(k): v.to_dict() for k, v in collections.items()}

    @field_serializer("progression")
    def _serialize_progression(self, progression: Progression) -> list[str]:
        return [str(item) for item in progression.order]

    def __contains__(self, item: ID.RefSeq) -> bool:
        """Check if item(s) exist in collection."""
        get_id = ID.get_id
        items = to_list(item, flatten=True, dropna=True, use_values=True)
        for i in items:
            try:
                item_id = get_id(i)
                if item_id not in self.collections:
                    return False
            except:
                return False
        return True

    def __setitem__(self, key: ID.RefSeq | int | slice, value: ID.ItemSeq):
        """Set item(s) at specified key/index."""
        item_dict = validate_collection_item_type(
            value, self.item_type, self.strict_type
        )
        new_ids = list(item_dict.keys())

        if isinstance(key, int):
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
            # Slices never IndexError, out-of-range slice returns empty
            # Check existence for new items
            slice_items = self.progression[key]  # current items in that slice
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
            # Key is refs
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
                    f"Invalid key {processed_key}. Key and item do not match."
                )

            # Check existence
            for i in new_ids:
                if i not in processed_key and i in self.collections:
                    raise ItemExistsError("Item already exists in the pile.")

            self.progression.include(processed_key)
            self.collections.update(item_dict)

    @synchronized
    def set(self, key: ID.RefSeq | int | slice, value: ID.ItemSeq):
        """Thread-safe set operation."""
        self[key] = value

    @async_synchronized
    async def aset(self, key: ID.RefSeq | int | slice, value: ID.ItemSeq):
        """Async thread-safe set operation."""
        self[key] = value

    def __getitem__(self, key: ID.RefSeq | int | slice) -> ID.ItemSeq:
        """Get item(s) by key/index."""
        try:
            if isinstance(key, (int, slice)):
                result_ids = self.progression[key]
                if not isinstance(result_ids, list):
                    result_ids = [result_ids]
                return (
                    self.collections[result_ids[0]]
                    if len(result_ids) == 1
                    else [self.collections[i] for i in result_ids]
                )

            # If key is not int or slice, treat as refs
            # Convert key to IDs
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
                # If parsing failed, no such item
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
        """Internal get implementation with default value handling."""
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
        """Include items without raising errors."""
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

    def _append(self, item: ID.ItemSeq):
        """will raise value error, if any item is not an Element"""
        item_dict = validate_collection_item_type(
            item, self.item_type, self.strict_type
        )
        if any(i in self.collections for i in item_dict):
            raise ItemExistsError("Item already exists in the pile.")
        self.progression.append(list(item_dict.keys()))
        self.collections.update(item_dict)

    @synchronized
    def append(self, item: ID.ItemSeq):
        """Thread-safe append operation."""
        self._append(item)

    def exclude(self, item: ID.RefSeq) -> bool:
        """Exclude items without raising errors."""
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
        """Internal pop implementation."""
        try:
            item_ids = []
            if isinstance(item, (int, slice)):
                item_ids = self.progression[item]
            else:
                item_ids = validate_order(item)
            out = []
            item_ids = (
                [item_ids] if not isinstance(item_ids, list) else item_ids
            )
            for i in item_ids:
                if i not in self.collections:
                    raise ItemNotFoundError(
                        f"Item with id {i} not found in the pile."
                    )
                out.append(self.collections.pop(i))
                self.progression.exclude(i)
            return out[0] if len(out) == 1 else out
        except Exception as e:
            if default is not UNDEFINED:
                return default
            raise ItemNotFoundError(
                f"Item with id {item} not found in the pile."
            ) from e

    @synchronized
    def popleft(self) -> E:
        """Thread-safe pop operation."""
        return self._pop(self.progression.popleft())

    @async_synchronized
    async def apopleft(self) -> E:
        return self._pop(self.progression.popleft())

    @synchronized
    def pop(
        self, item: ID.RefSeq = 0, default: D = UNDEFINED
    ) -> E | list[E] | D:
        """Thread-safe pop operation."""
        return self._pop(item, default)

    @async_synchronized
    async def apop(
        self, item: ID.RefSeq = 0, default: D = UNDEFINED
    ) -> E | list[E] | D:
        """Async thread-safe pop operation."""
        return self._pop(item, default)

    def __getstate__(self):
        """Get state for pickling."""
        state = self.__dict__.copy()
        state["_lock"] = None
        state["_async_lock"] = None
        return state

    def __setstate__(self, state):
        """Set state for unpickling."""
        self.__dict__.update(state)
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    @property
    def lock(self) -> threading.Lock:
        """Thread lock for synchronization."""
        if not hasattr(self, "_lock") or self._lock is None:
            self._lock = threading.Lock()
        return self._lock

    @property
    def async_lock(self) -> asyncio.Lock:
        """Async lock for synchronization."""
        if not hasattr(self, "_async_lock") or self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    def __iter__(self) -> Iterator[E]:
        """Iterate over items safely."""
        with self.lock:
            current_order = list(self.progression)

        for key in current_order:
            yield self.collections[key]

    def keys(self) -> Generator[IDType]:
        """Get ordered list of collection keys."""
        return (i for i in self.progression.order[:])

    def values(self) -> Generator[E]:
        """Get ordered list of collection values."""
        return (self.collections[i] for i in list(self.progression))

    def items(self) -> Generator[tuple[IDType, E]]:
        """Get collection items as key-value pairs."""
        return ((i, self.collections[i]) for i in self.progression)

    @synchronized
    def insert(self, index: int, item: ID.Item):
        """Insert item at specified index without replacing existing items.

        Args:
            index: Position to insert at.
            item: Item(s) to insert.

        Raises:
            ItemExistsError: If item already exists in collection.
        """
        item_dict = validate_collection_item_type(
            item, self.item_type, self.strict_type
        )
        for i in item_dict:
            if i in self.progression:
                raise ItemExistsError(f"item {i} already exists in the pile")
        self.progression.insert(index, list(item_dict.keys()))
        self.collections.update(item_dict)

    def _clear(self):
        self.collections.clear()
        self.progression.clear()

    @synchronized
    def clear(self):
        """Remove all items from collection."""
        self._clear()

    @async_synchronized
    async def aclear(self):
        """Async clear operation."""
        self._clear()

    def _update(self, other: ID.ItemSeq | ID.Item):
        # Update or include new items
        items = to_list(other, flatten=True, dropna=True, use_values=True)
        # must be Elements
        if any(not isinstance(x, Element) for x in items):
            raise ValueError("All items must be Element instances.")
        others = {x.id: x for x in items}
        for i, val in others.items():
            if i in self.collections:
                self.collections[i] = val
            else:
                self.include(val)

    def update(self, other: ID.ItemSeq | ID.Item):
        """Update existing items or include new ones."""
        self._update(other)

    @async_synchronized
    async def aupdate(self, other: ID.ItemSeq | ID.Item):
        """Async update operation."""
        self._update(other)

    async def __aiter__(self) -> AsyncIterator[E]:
        """Async iterate over items."""
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
        """Async context manager entry."""
        await self.async_lock.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        self.async_lock.release()

    def __len__(self) -> int:
        """Get collection size."""
        return len(self.collections)

    def __list__(self) -> list[E]:
        return list(self.values())

    def __or__(self, other: Pile) -> Pile:
        """Create a new Pile containing items from both piles (union).

        Returns items present in either current pile or other pile.
        Original piles remain unchanged.

        Args:
            other: Pile to union with.

        Returns:
            Pile: New pile containing all items from both piles.

        Raises:
            ValueError: If other is not a Pile or items don't match item_type.

        Example:
            >>> pile1 = Pile([item1, item2])
            >>> pile2 = Pile([item2, item3])
            >>> result = pile1 | pile2  # Contains item1, item2, item3
        """
        if not isinstance(other, Pile):
            raise ValueError("Only Pile instances can be unioned.")
        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            raise ValueError(
                "All items must be exactly of type {self.item_type}."
            )
        result = self.__class__(
            collections=self.collections,
            item_type=self.item_type,
            strict_type=self.strict_type,
            progression=self.progression,
        )
        result._update(other)
        return result

    def __ior__(self, other: Pile) -> Self:
        """Add all items from other pile into this pile (in-place union).

        Updates current pile with items from other pile. Other pile
        remains unchanged.

        Args:
            other: Pile to union with.

        Returns:
            Self: Updated current pile with items from both piles.

        Raises:
            ValueError: If other is not a Pile or items don't match item_type.

        Example:
            >>> pile1 = Pile([item1, item2])
            >>> pile2 = Pile([item2, item3])
            >>> pile1 |= pile2  # pile1 now contains item1, item2, item3
        """
        if not isinstance(other, Pile):
            raise ValueError("Only Pile instances can be unioned.")
        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            raise ValueError(
                "All items must be exactly of type {self.item_type}."
            )
        other = validate_collection_item_type(
            other, self.item_type, self.strict_type
        )
        self._update(other)
        return self

    def __xor__(self, other: Pile) -> Pile:
        """Create new Pile with items in either pile but not both (symmetric difference).

        Returns items that are present in only one of the piles, excluding items
        present in both. Original piles remain unchanged.

        Args:
            other: Pile to compute symmetric difference with.

        Returns:
            Pile: New pile containing items unique to each pile.

        Raises:
            ValueError: If other is not a Pile or items don't match item_type.

        Example:
            >>> pile1 = Pile([item1, item2])
            >>> pile2 = Pile([item2, item3])
            >>> result = pile1 ^ pile2  # Contains only item1, item3
        """
        if not isinstance(other, Pile):
            raise ValueError(
                "Only Pile instances can be symmetric differenced."
            )
        if self.item_type:
            other = validate_collection_item_type(
                list(other), self.item_type, self.strict_type
            )
            raise ValueError(
                "All items must be exactly of type {self.item_type}."
            )

        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        values = [i for i in self if i not in to_exclude] + [
            i for i in other if i not in to_exclude
        ]

        result = self.__class__(
            collections=values,
            item_type=self.item_type,
            strict_type=self.strict_type,
        )
        return result

    def __ixor__(self, other: Pile) -> Self:
        """Update pile with items in either pile but not both (in-place symmetric difference).

        Modifies current pile to contain only items unique to each pile,
        removing items present in both. Other pile remains unchanged.

        Args:
            other: Pile to compute symmetric difference with.

        Returns:
            Self: Updated current pile with symmetric difference result.

        Raises:
            ValueError: If other is not a Pile or items don't match item_type.

        Example:
            >>> pile1 = Pile([item1, item2])
            >>> pile2 = Pile([item2, item3])
            >>> pile1 ^= pile2  # pile1 now contains only item1, item3
        """
        if not isinstance(other, Pile):
            raise ValueError(
                "Only Pile instances can be symmetric differenced."
            )

        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            raise ValueError(
                "All items must be exactly of type {self.item_type}."
            )
        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        other = [i for i in other if i not in to_exclude]
        self.exclude(to_exclude)
        self.include(other)
        return self

    def __iand__(self, other: Pile) -> Self:
        """Update pile to keep only items present in both piles (in-place intersection).

        Modifies current pile to contain only items that exist in both piles.
        Other pile remains unchanged.

        Args:
            other: Pile to intersect with.

        Returns:
            Self: Updated current pile with intersection result.

        Raises:
            ValueError: If other is not a Pile or items don't match item_type.

        Example:
            >>> pile1 = Pile([item1, item2])
            >>> pile2 = Pile([item2, item3])
            >>> pile1 &= pile2  # pile1 now contains only item2
        """
        if not isinstance(other, Pile):
            raise ValueError(
                "Only Pile instances can be symmetric differenced."
            )

        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            raise ValueError(
                "All items must be exactly of type {self.item_type}."
            )

        to_exclude = []
        for i in self.values():
            if i not in other:
                to_exclude.append(i)
        self.exclude(to_exclude)
        return self

    def __and__(self, other: Pile) -> Pile:
        """Create new Pile containing items present in both piles (intersection).

        Returns only items that exist in both the current pile and other pile.
        Original piles remain unchanged.

        Args:
            other: Pile to intersect with.

        Returns:
            Pile: New pile containing only items present in both piles.

        Raises:
            ValueError: If other is not a Pile or items don't match item_type.

        Example:
            >>> pile1 = Pile([item1, item2])
            >>> pile2 = Pile([item2, item3])
            >>> result = pile1 & pile2  # Contains only item2
        """
        if not isinstance(other, Pile):
            raise ValueError(
                "Only Pile instances can be symmetric differenced."
            )

        if self.item_type and any(
            not isinstance(x, self.item_type) for x in other
        ):
            raise ValueError(
                "All items must be exactly of type {self.item_type}."
            )

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
        """kwargs for self.to_dict(), check pd.DataFrame.from_records for pd.DataFrame kwargs, check pydantic.BaseModel.model_dump() for self.to_dict() kwargs"""
        dicts_ = [i.to_dict(**kwargs) for i in self.values()]
        return pd.DataFrame.from_records(
            dicts_,
            index=index,
            exclude=exclude,
            columns=columns,
            coerce_float=coerce_float,
            nrows=nrows,
        )

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
    ):
        """Export collection to CSV file.

        Args:
            path_or_buf: File path or buffer to write to.
            verbose: Print confirmation message.
            Other arguments passed to pandas.DataFrame.to_csv().
        """
        self.to_df().to_csv(**locals())
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
    ):
        """Export collection to JSON file.

        Args:
            path_or_buf: File path or buffer to write to.
            use_pd: Use pandas JSON export if True.
            mode: File open mode.
            verbose: Print confirmation message.
            **kwargs: Additional arguments for json.dump() or DataFrame.to_json().
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
    ):
        """Export collection to file and optionally clear.

        Args:
            path_or_buf: File path or buffer to write to.
            file_type: Format to export as ("json" or "csv").
            clear: Clear collection after export if True.
            verbose: Print confirmation message.
            **kwargs: Additional export arguments.
                - For JSON: if use_pd (bool), mode (str), **kwargs for pd.DataFrame.to_json() or json.dump().
                - For CSV: **kwargs for pd.DataFrame.to_csv().
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
    ):
        """Async dump operation."""
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
        """Create new Pile instance.

        Args:
            collections: Initial items.
            item_type: Type constraint for items.
            strict_type: Enforce exact type matching.
            progression: Custom item ordering.

        Returns:
            New Pile instance.
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
        """Get next item in iteration."""
        try:
            return next(iter(self))
        except StopIteration:
            raise StopIteration("End of pile")

    def __str__(self) -> str:
        """String representation as DataFrame."""
        return str(self.to_df())

    def __repr__(self) -> str:
        """Detailed string representation."""
        length = len(self)
        if length == 0:
            return "Pile()"
        if length == 1:
            return f"Pile({next(iter(self.collections.values())).__repr__()})"
        return repr(self.to_df())

    def __bool__(self) -> bool:
        """Check if pile is empty."""
        return bool(self.collections)


def pile(
    collections: ID.ItemSeq,
    item_type: type = None,
    strict_type: bool = False,
    progression: Progression | ID.RefSeq = None,
) -> Pile:
    """Convenience function to create a new Pile instance."""
    return Pile.create(
        collections,
        item_type=item_type,
        strict_type=strict_type,
        progression=progression,
    )


# File: lionagi/protocols/pile.py
