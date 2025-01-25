# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
import threading
from collections import deque
from collections.abc import (
    AsyncIterator,
    Callable,
    Generator,
    Iterator,
    Sequence,
)
from functools import wraps
from pathlib import Path
from typing import Any, ClassVar, Generic, TypeVar

import pandas as pd
from pydantic import Field, field_serializer
from pydantic.fields import FieldInfo
from typing_extensions import Self, override

from lionagi._errors import ItemExistsError, ItemNotFoundError
from lionagi.utils import UNDEFINED, is_same_dtype, to_list

from .._concepts import Observable
from ..adapters.adapter import Adapter, AdapterRegistry
from ..adapters.json_adapter import JsonAdapter, JsonFileAdapter
from ..adapters.pandas_.csv_adapter import CSVFileAdapter
from ..adapters.pandas_.excel_adapter import ExcelFileAdapter
from ..adapters.pandas_.pd_dataframe_adapter import PandasDataFrameAdapter
from .element import ID, Collective, E, Element, IDType, validate_order
from .progression import Progression

D = TypeVar("D")
T = TypeVar("T", bound=E)


PILE_DEFAULT_ADAPTERS = (
    JsonAdapter,
    JsonFileAdapter,
    CSVFileAdapter,
    ExcelFileAdapter,
    PandasDataFrameAdapter,
)


class PileAdapterRegistry(AdapterRegistry):
    pass


for i in PILE_DEFAULT_ADAPTERS:
    PileAdapterRegistry.register(i)


__all__ = (
    "Pile",
    "pile",
)


def synchronized(func: Callable):
    @wraps(func)
    def wrapper(self: Pile, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)

    return wrapper


def async_synchronized(func: Callable):
    @wraps(func)
    async def wrapper(self: Pile, *args, **kwargs):
        async with self.async_lock:
            return await func(self, *args, **kwargs)

    return wrapper


class Pile(Element, Collective[E], Generic[E]):
    """Thread-safe async-compatible, ordered collection of elements.

    The Pile class provides a thread-safe, async-compatible collection with:
    - Type validation and enforcement
    - Order preservation
    - Format adapters (JSON, CSV, Excel)
    - Memory efficient storage

    Attributes:
        pile_ (dict[str, T]): Internal storage mapping IDs to elements
        item_type (set[type[T]] | None): Allowed element types
        progress (Progression): Order tracking
        strict_type (bool): Whether to enforce strict type checking
    """

    collections: dict[IDType, T] = Field(default_factory=dict)
    item_type: set | None = Field(
        default=None,
        description="Set of allowed types for items in the pile.",
        exclude=True,
    )
    progression: Progression = Field(
        default_factory=Progression,
        description="Progression specifying the order of items in the pile.",
        exclude=True,
    )
    strict_type: bool = Field(
        default=False,
        description="Specify if enforce a strict type check",
        frozen=True,
    )

    _adapter_registry: ClassVar[AdapterRegistry] = PileAdapterRegistry

    def __pydantic_extra__(self) -> dict[str, FieldInfo]:
        return {
            "_lock": Field(default_factory=threading.Lock),
            "_async": Field(default_factory=asyncio.Lock),
        }

    def __pydantic_private__(self) -> dict[str, FieldInfo]:
        return self.__pydantic_extra__()

    @override
    def __init__(
        self,
        collections: ID.ItemSeq = None,
        item_type: set[type[T]] = None,
        order: ID.RefSeq = None,
        strict_type: bool = False,
        **kwargs,
    ) -> None:
        """Initialize a Pile instance.

        Args:
            items: Initial items for the pile.
            item_type: Allowed types for items in the pile.
            order: Initial order of items (as Progression).
            strict_type: If True, enforce strict type checking.
        """
        _config = {}
        if "id" in kwargs:
            _config["id"] = kwargs["id"]
        if "created_at" in kwargs:
            _config["created_at"] = kwargs["created_at"]

        super().__init__(strict_type=strict_type, **_config)
        self.item_type = self._validate_item_type(item_type)

        if isinstance(collections, list) and is_same_dtype(collections, dict):
            collections = [Element.from_dict(i) for i in collections]

        self.collections = self._validate_pile(
            collections or kwargs.get("collections", {})
        )
        self.progression = self._validate_order(order)

    # Sync Interface methods
    @override
    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        /,
    ) -> Pile:
        """Create a Pile instance from a dictionary.

        Args:
            data: A dictionary containing Pile data.

        Returns:
            A new Pile instance created from the provided data.

        Raises:
            ValueError: If the dictionary format is invalid.
        """
        items = data.pop("collections", [])
        items = [Element.from_dict(i) for i in items]
        return cls(collections=items, **data)

    def __setitem__(
        self,
        key: ID.Ref | ID.RefSeq | int | slice,
        item: ID.ItemSeq | ID.Item,
    ) -> None:
        """Set an item or items in the Pile.

        Args:
            key: The key to set (index, ID, or slice).
            item: The item(s) to set.

        Raises:
            TypeError: If item type not allowed.
            KeyError: If key invalid.
        """
        self._setitem(key, item)

    @synchronized
    def pop(
        self,
        key: ID.Ref | ID.RefSeq | int | slice,
        default: D = UNDEFINED,
        /,
    ) -> T | Pile | D:
        """Remove and return item(s) from the Pile.

        Args:
            key: Key of item(s) to remove.
            default: Value if key not found.

        Returns:
            Removed item(s) or default.

        Raises:
            KeyError: If key not found and no default.
        """
        return self._pop(key, default)

    def remove(
        self,
        item: T,
        /,
    ) -> None:
        """Remove a specific item from the Pile.

        Args:
            item: Item to remove.

        Raises:
            ValueError: If item not found.
        """
        self._remove(item)

    def include(
        self,
        item: ID.ItemSeq | ID.Item,
        /,
    ) -> None:
        """Include item(s) if not present.

        Args:
            item: Item(s) to include.

        Raises:
            TypeError: If item type not allowed.
        """
        self._include(item)

    def exclude(
        self,
        item: ID.ItemSeq | ID.Item,
        /,
    ) -> None:
        """Exclude item(s) if present.

        Args:
            item: Item(s) to exclude.
        """
        self._exclude(item)

    @synchronized
    def clear(self) -> None:
        """Remove all items."""
        self._clear()

    def update(
        self,
        other: ID.Item | ID.ItemSeq,
        /,
    ) -> None:
        """Update with items from another source.

        Args:
            other: Items to update from.

        Raises:
            TypeError: If item types not allowed.
        """
        self._update(other)

    @synchronized
    def insert(self, index: int, item: T, /) -> None:
        """Insert item at position.

        Args:
            index: Position to insert at.
            item: Item to insert.

        Raises:
            IndexError: If index out of range.
            TypeError: If item type not allowed.
        """
        self._insert(index, item)

    @synchronized
    def append(self, item: T, /) -> None:
        """Append item to end (alias for include).

        Args:
            item: Item to append.

        Raises:
            TypeError: If item type not allowed.
        """
        self.update(item)

    @synchronized
    def get(
        self,
        key: ID.Ref | ID.RefSeq | int | slice,
        default: D = UNDEFINED,
        /,
    ) -> T | Pile | D:
        """Get item(s) by key with default.

        Args:
            key: Key to get items by.
            default: Value if not found.

        Returns:
            Item(s) or default.
        """
        return self._get(key, default)

    def keys(self) -> Sequence[str]:
        """Get all Lion IDs in order."""
        return list(self.progression)

    def values(self) -> Sequence[T]:
        """Get all items in order."""
        return [self.collections[key] for key in self.progression]

    def items(self) -> Sequence[tuple[IDType, T]]:
        """Get all (ID, item) pairs in order."""
        return [(key, self.collections[key]) for key in self.progression]

    def is_empty(self) -> bool:
        """Check if empty."""
        return len(self.progression) == 0

    def size(self) -> int:
        """Get number of items."""
        return len(self.progression)

    def __iter__(self) -> Iterator[T]:
        """Iterate over items safely."""
        with self.lock:
            current_order = list(self.progression)

        for key in current_order:
            yield self.collections[key]

    def __next__(self) -> T:
        """Get next item."""
        try:
            return next(iter(self))
        except StopIteration:
            raise StopIteration("End of pile")

    def __getitem__(
        self, key: ID.Ref | ID.RefSeq | int | slice
    ) -> Any | list | T:
        """Get item(s) by key.

        Args:
            key: Key to get items by.

        Returns:
            Item(s) or sliced Pile.

        Raises:
            KeyError: If key not found.
        """
        return self._getitem(key)

    def __contains__(self, item: ID.RefSeq | ID.Ref) -> bool:
        """Check if item exists."""
        return item in self.progression

    def __len__(self) -> int:
        """Get number of items."""
        return len(self.collections)

    @override
    def __bool__(self) -> bool:
        """Check if not empty."""
        return not self.is_empty()

    def __list__(self) -> list[T]:
        """Convert to list."""
        return self.values()

    def __ior__(self, other: Pile) -> Self:
        """In-place union."""
        if not isinstance(other, Pile):
            raise TypeError(
                f"Invalid type for Pile operation. expected <Pile>, got {type(other)}"
            )
        other = self._validate_pile(list(other))
        self.include(other)
        return self

    def __or__(self, other: Pile) -> Pile:
        """Union."""
        if not isinstance(other, Pile):
            raise TypeError(
                f"Invalid type for Pile operation. expected <Pile>, got {type(other)}"
            )

        result = self.__class__(
            items=self.values(),
            item_type=self.item_type,
            order=self.progression,
        )
        result.include(list(other))
        return result

    def __ixor__(self, other: Pile) -> Self:
        """In-place symmetric difference."""
        if not isinstance(other, Pile):
            raise TypeError(
                f"Invalid type for Pile operation. expected <Pile>, got {type(other)}"
            )

        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        other = [i for i in other if i not in to_exclude]
        self.exclude(to_exclude)
        self.include(other)
        return self

    def __xor__(self, other: Pile) -> Pile:
        """Symmetric difference."""
        if not isinstance(other, Pile):
            raise TypeError(
                f"Invalid type for Pile operation. expected <Pile>, got {type(other)}"
            )

        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        values = [i for i in self if i not in to_exclude] + [
            i for i in other if i not in to_exclude
        ]

        result = self.__class__(
            items=values,
            item_type=self.item_type,
        )
        return result

    def __iand__(self, other: Pile) -> Self:
        """In-place intersection."""
        if not isinstance(other, Pile):
            raise TypeError(
                f"Invalid type for Pile operation. expected <Pile>, got {type(other)}"
            )

        to_exclude = []
        for i in self.values():
            if i not in other:
                to_exclude.append(i)
        self.exclude(to_exclude)
        return self

    def __and__(self, other: Pile) -> Pile:
        """Intersection."""
        if not isinstance(other, Pile):
            raise TypeError(
                f"Invalid type for Pile operation. expected <Pile>, got {type(other)}"
            )

        values = [i for i in self if i in other]
        return self.__class__(
            items=values,
            item_type=self.item_type,
        )

    @override
    def __str__(self) -> str:
        """Simple string representation."""
        return f"Pile({len(self)})"

    @override
    def __repr__(self) -> str:
        """Detailed string representation."""
        length = len(self)
        if length == 0:
            return "Pile()"
        elif length == 1:
            return f"Pile({next(iter(self.collections.values())).__repr__()})"
        else:
            return f"Pile({length})"

    def __getstate__(self):
        """Prepare for pickling."""
        state = self.__dict__.copy()
        state["_lock"] = None
        state["_async_lock"] = None
        return state

    def __setstate__(self, state):
        """Restore after unpickling."""
        self.__dict__.update(state)
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    @property
    def lock(self):
        """Thread lock."""
        if not hasattr(self, "_lock") or self._lock is None:
            self._lock = threading.Lock()
        return self._lock

    @property
    def async_lock(self):
        """Async lock."""
        if not hasattr(self, "_async_lock") or self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    # Async Interface methods
    @async_synchronized
    async def asetitem(
        self,
        key: ID.Ref | ID.RefSeq | int | slice,
        item: ID.Item | ID.ItemSeq,
        /,
    ) -> None:
        """Async set item(s)."""
        self._setitem(key, item)

    @async_synchronized
    async def apop(
        self,
        key: ID.Ref | ID.RefSeq | int | slice,
        default: Any = UNDEFINED,
        /,
    ):
        """Async remove and return item(s)."""
        return self._pop(key, default)

    @async_synchronized
    async def aremove(
        self,
        item: ID.Ref | ID.RefSeq,
        /,
    ) -> None:
        """Async remove item."""
        self._remove(item)

    @async_synchronized
    async def ainclude(
        self,
        item: ID.ItemSeq | ID.Item,
        /,
    ) -> None:
        """Async include item(s)."""
        self._include(item)
        if item not in self:
            raise TypeError(f"Item {item} is not of allowed types")

    @async_synchronized
    async def aexclude(
        self,
        item: ID.Ref | ID.RefSeq,
        /,
    ) -> None:
        """Async exclude item(s)."""
        self._exclude(item)

    @async_synchronized
    async def aclear(self) -> None:
        """Async clear all items."""
        self._clear()

    @async_synchronized
    async def aupdate(
        self,
        other: ID.ItemSeq | ID.Item,
        /,
    ) -> None:
        """Async update with items."""
        self._update(other)

    @async_synchronized
    async def aget(
        self,
        key: Any,
        default=UNDEFINED,
        /,
    ) -> list | Any | T:
        """Async get item(s)."""
        return self._get(key, default)

    async def __aiter__(self) -> AsyncIterator[T]:
        """Async iterate over items."""
        async with self.async_lock:
            current_order = list(self.progression)

        for key in current_order:
            yield self.collections[key]
            await asyncio.sleep(0)  # Yield control to the event loop

    async def __anext__(self) -> T:
        """Async get next item."""
        try:
            return await anext(self.AsyncPileIterator(self))
        except StopAsyncIteration:
            raise StopAsyncIteration("End of pile")

    # private methods
    def _getitem(self, key: Any) -> Any | list | T:
        if key is None:
            raise ValueError("getitem key not provided.")

        if isinstance(key, int | slice):
            try:
                result_ids = self.progression[key]
                result_ids = (
                    [result_ids]
                    if not isinstance(result_ids, list)
                    else result_ids
                )
                result = []
                for i in result_ids:
                    result.append(self.collections[i])
                return result[0] if len(result) == 1 else result
            except Exception as e:
                raise ItemNotFoundError(f"index {key}. Error: {e}")

        elif isinstance(key, IDType):
            try:
                return self.collections[key]
            except Exception as e:
                raise ItemNotFoundError(f"key {key}. Error: {e}")

        else:
            key = to_list_type(key)
            result = []
            try:
                for k in key:
                    result_id = ID.get_id(k)
                    result.append(self.collections[result_id])

                if len(result) == 0:
                    raise ItemNotFoundError(f"key {key} item not found")
                if len(result) == 1:
                    return result[0]
                return result
            except Exception as e:
                raise ItemNotFoundError(f"Key {key}. Error:{e}")

    def _setitem(
        self,
        key: ID.Ref | ID.RefSeq | int | slice,
        item: ID.Item | ID.ItemSeq,
    ) -> None:
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i in self.progression:
                raise ItemExistsError(f"item {i} already exists in the pile")
            item_order.append(i)
        if isinstance(key, int | slice):
            try:
                delete_order = (
                    list(self.progression[key])
                    if isinstance(self.progression[key], Progression)
                    else [self.progression[key]]
                )
                self.progression[key] = item_order
                for i in to_list(delete_order, flatten=True):
                    self.collections.pop(i)
                self.collections.update(item_dict)
            except Exception as e:
                raise ValueError(f"Failed to set pile. Error: {e}")
        else:
            key = to_list_type(key)
            if isinstance(key[0], list):
                key = to_list(key, flatten=True, dropna=True)
            if len(key) != len(item_order):
                raise KeyError(
                    f"Invalid key {key}. Key and item does not match.",
                )
            for k in key:
                id_ = ID.get_id(k)
                if id_ not in item_order:
                    raise KeyError(
                        f"Invalid key {id_}. Key and item does not match.",
                    )
            self.progression += key
            self.collections.update(item_dict)

    def _get(self, key: Any, default: D = UNDEFINED) -> T | Pile | D:
        if isinstance(key, int | slice):
            try:
                return self[key]
            except Exception as e:
                if default is UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default
        else:
            check = None
            if isinstance(key, list):
                check = True
                for i in key:
                    if type(i) is not int:
                        check = False
                        break
            try:
                if not check:
                    key = validate_order(key)
                result = []
                for k in key:
                    result.append(self[k])
                if len(result) == 0:
                    raise ItemNotFoundError(f"key {key} item not found")
                if len(result) == 1:
                    return result[0]
                return result

            except Exception as e:
                if default is UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default

    def _pop(
        self,
        key: ID.Ref | ID.RefSeq | int | slice,
        default: D = UNDEFINED,
    ) -> T | Pile | D:
        if isinstance(key, int | slice):
            try:
                pops = self.progression[key]
                pops = [pops] if isinstance(pops, IDType) else pops
                result = []
                for i in pops:
                    self.progression.remove(i)
                    result.append(self.collections.pop(i))
                result = (
                    self.__class__(items=result, item_type=self.item_type)
                    if len(result) > 1
                    else result[0]
                )
                return result
            except Exception as e:
                if default is UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default
        else:
            try:
                key = validate_order(key)
                result = []
                for k in key:
                    self.progression.remove(k)
                    result.append(self.collections.pop(k))
                if len(result) == 0:
                    raise ItemNotFoundError(f"key {key} item not found")
                elif len(result) == 1:
                    return result[0]
                return result
            except Exception as e:
                if default is UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default

    def _remove(self, item: ID.Ref | ID.RefSeq):
        if isinstance(item, int | slice):
            raise TypeError(
                "Invalid item type for remove, should be ID or Item(s)"
            )
        if item in self:
            self.pop(item)
            return
        raise ItemNotFoundError(f"{item}")

    def _include(self, item: ID.ItemSeq | ID.Item):
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i not in self.progression:
                item_order.append(i)

        self.progression.append(item_order)
        self.collections.update(item_dict)

    def _exclude(self, item: ID.Ref | ID.RefSeq):
        item = to_list_type(item)
        exclude_list = []
        for i in item:
            if i in self:
                exclude_list.append(i)
        if exclude_list:
            self.pop(exclude_list)

    def _clear(self) -> None:
        self.collections.clear()
        self.progression.clear()

    def _update(self, other: ID.ItemSeq | ID.Item):
        others = self._validate_pile(other)
        for i in others.keys():
            if i in self.collections:
                self.collections[i] = others[i]
            else:
                self.include(others[i])

    def _validate_item_type(self, value) -> set[type[T]] | None:
        if value is None:
            return None

        value = to_list_type(value)

        for i in value:
            if not issubclass(i, Observable):
                raise TypeError(
                    f"Item type must be a subclass of Observable. Got {i}"
                )

        if len(value) != len(set(value)):
            raise ValueError(
                "Detected duplicated item types in item_type.",
            )

        if len(value) > 0:
            return set(value)

    def _validate_pile(self, value: Any) -> dict[str, T]:
        if not value:
            return {}

        value = to_list_type(value)

        result = {}
        for i in value:
            if isinstance(i, dict):
                i = Element.from_dict(i)

            if self.item_type:
                if self.strict_type:
                    if type(i) not in self.item_type:
                        raise TypeError(
                            "Invalid item type in pile."
                            f" Expected {self.item_type}",
                        )
                else:
                    if not any(issubclass(type(i), t) for t in self.item_type):
                        raise TypeError(
                            "Invalid item type in pile. Expected "
                            f"{self.item_type} or the subclasses",
                        )
            else:
                if not isinstance(i, Observable):
                    raise ValueError(f"Invalid pile item {i}")

            result[i.id] = i

        return result

    def _validate_order(self, value: Any) -> Progression:
        if not value:
            return self.progression.__class__(
                order=list(self.collections.keys())
            )

        if isinstance(value, Progression):
            value = list(value)
        else:
            value = to_list_type(value)

        value_set = set(value)
        if len(value_set) != len(value):
            raise ValueError("There are duplicate elements in the order")
        if len(value_set) != len(self.collections.keys()):
            raise ValueError(
                "The length of the order does not match the length of the pile"
            )

        for i in value_set:
            if ID.get_id(i) not in self.collections.keys():
                raise ValueError(
                    f"The order does not match the pile. {i} not found"
                )

        return self.progression.__class__(order=value)

    def _insert(self, index: int, item: ID.Item):
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i in self.progression:
                raise ItemExistsError(f"item {i} already exists in the pile")
            item_order.append(i)
        self.progression.insert(index, item_order)
        self.collections.update(item_dict)

    @field_serializer("collections")
    def _(self, value: dict[str, T]):
        return [i.to_dict() for i in value.values()]

    class AsyncPileIterator:
        def __init__(self, pile: Pile):
            self.pile = pile
            self.index = 0

        def __aiter__(self) -> AsyncIterator[T]:
            return self

        async def __anext__(self) -> T:
            if self.index >= len(self.pile):
                raise StopAsyncIteration
            item = self.pile[self.pile.progression[self.index]]
            self.index += 1
            await asyncio.sleep(0)  # Yield control to the event loop
            return item

    async def __aenter__(self) -> Self:
        """Enter async context."""
        await self.async_lock.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit async context."""
        self.async_lock.release()

    def is_homogenous(self) -> bool:
        """Check if all items are same type."""
        return len(self.collections) < 2 or all(
            is_same_dtype(self.collections.values())
        )

    def adapt_to(self, obj_key: str, /, **kwargs: Any) -> Any:
        """Convert to another format."""
        return self._get_adapter_registry().adapt_to(self, obj_key, **kwargs)

    @classmethod
    def list_adapters(cls):
        """List available adapters."""
        return cls._get_adapter_registry().list_adapters()

    @classmethod
    def register_adapter(cls, adapter: type[Adapter]):
        """Register new adapter."""
        cls._get_adapter_registry().register(adapter)

    @classmethod
    def _get_adapter_registry(cls) -> AdapterRegistry:
        if isinstance(cls._adapter_registry, type):
            cls._adapter_registry = cls._adapter_registry()
        return cls._adapter_registry

    @classmethod
    def adapt_from(cls, obj: Any, obj_key: str, /, **kwargs: Any):
        """Create from another format."""
        dict_ = cls._get_adapter_registry().adapt_from(
            cls, obj, obj_key, **kwargs
        )
        if isinstance(dict_, list):
            dict_ = {"collections": dict_}
        return cls.from_dict(dict_)

    def to_df(
        self,
        columns: list[str] | None = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Convert to DataFrame."""
        return self.adapt_to("pd_dataframe", columns=columns, **kwargs)

    def to_csv_file(self, fp: str | Path, **kwargs: Any) -> None:
        """Save to CSV file."""
        self.adapt_to(".csv", fp=fp, **kwargs)

    def to_json_file(
        self,
        path_or_buf,
        *,
        use_pd: bool = False,
        many: bool = False,
        mode="w",
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
        return self.adapt_to(".json", fp=path_or_buf, mode=mode, many=many)


def pile(
    collections: Any = None,
    /,
    item_type: type[T] | set[type[T]] | None = None,
    progression: list[str] | None = None,
    strict_type: bool = False,
    df: pd.DataFrame | None = None,  # priority 1
    fp: str | Path | None = None,  # priority 2
    **kwargs,
) -> Pile:
    """Create a new Pile instance.

    Args:
        items: Initial items for the pile.
        item_type: Allowed types for items in the pile.
        order: Initial order of items.
        strict: If True, enforce strict type checking.

    Returns:
        Pile: A new Pile instance.
    """

    if df:
        return Pile.adapt_from(df, "pd_dataframe", **kwargs)

    if fp:
        fp = Path(fp)
        if fp.suffix == ".csv":
            return Pile.adapt_from(fp, ".csv", **kwargs)
        if fp.suffix == ".xlsx":
            return Pile.adapt_from(fp, ".xlsx", **kwargs)
        if fp.suffix in [".json", ".jsonl"]:
            return Pile.adapt_from(fp, ".json", **kwargs)

    return Pile(
        collections,
        item_type=item_type,
        order=progression,
        strict=strict_type,
        **kwargs,
    )


def to_list_type(value: Any, /) -> list[Any]:
    """Convert input to a list format"""
    if value is None:
        return []
    if isinstance(value, IDType):
        return [value]
    if isinstance(value, str):
        return ID.get_id(value) if ID.is_id(value) else []
    if isinstance(value, Element):
        return [value]
    if hasattr(value, "values") and callable(value.values):
        return list(value.values())
    if isinstance(value, list | tuple | set | deque | Generator):
        return list(value)
    return [value]


# File: lionagi/protocols/generic/pile.py
