# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import logging
import threading
from collections.abc import AsyncIterator, Callable, Iterator
from functools import wraps
from pathlib import Path
from typing import Any, ClassVar, Generic, Self, TypeVar

import pandas as pd

from lionagi._class_registry import get_class
from lionagi._errors import ItemExistsError, ItemNotFoundError
from lionagi.utils import UNDEFINED, to_list

from .._adapter import DEFAULT_ADAPTERS, Adaptable, AdapterRegistry
from .concepts import Collective
from .element import Element, IDType
from .progression import Progression, validate_order

E = TypeVar("E", bound=Element)


def validate_collection_item_type(
    collections: Any,
    item_type: type[E] | None = None,
    strict_type: bool = False,
) -> dict[IDType, Element]:
    """
    Convert an input into dict[IDType, Element], enforcing:
      - Items must be `Element` instances
      - Optionally, items must match `item_type` exactly (if strict_type=True)
        or at least be an instance of `item_type` (if strict_type=False).
    """
    items = to_list(collections, flatten=True, dropna=True, use_values=True)
    if item_type is not None:
        if strict_type:
            for x in items:
                if type(x) is not item_type:
                    raise TypeError(
                        f"Items must match type exactly: {item_type}."
                    )
        else:
            for x in items:
                if not isinstance(x, item_type):
                    raise TypeError(f"Items must be instances of {item_type}.")

    out = {}
    for x in items:
        if not isinstance(x, Element):
            raise ValueError("All items must be Element instances.")
        out[x.id] = x
    return out


def synchronized(func: Callable):
    """Decorator for thread-safe synchronous methods."""

    @wraps(func)
    def wrapper(self: "Pile", *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)

    return wrapper


def async_synchronized(func: Callable):
    """Decorator for thread-safe asynchronous methods."""

    @wraps(func)
    async def wrapper(self: "Pile", *args, **kwargs):
        async with self.async_lock:
            return await func(self, *args, **kwargs)

    return wrapper


class PileAdapterRegistry(AdapterRegistry):
    """Registry for Pile adapters."""


for adapter in DEFAULT_ADAPTERS:
    PileAdapterRegistry.register(adapter)


class Pile(Element, Adaptable, Collective[E], Generic[E]):
    """
    Thread-safe collection of Elements, keyed by ID, plus a `Progression`
    for item ordering.

    - `include` / `exclude` match `Progression` semantics:
      - return bool indicating whether any items were actually added/removed
      - ignore duplicates (in `include`) or missing items (in `exclude`)
      - do not raise errors
    - `append` / `remove` / `insert` are stricter:
      - raise `ItemExistsError` or `ItemNotFoundError` if appropriate
    """

    adapter_registry: ClassVar[AdapterRegistry] = PileAdapterRegistry

    def __init__(
        self,
        collections: Any = None,
        item_type: type[E] | None = None,
        strict_type: bool = False,
        progression: Progression | list[IDType] | None = None,
        **kwargs: Any,
    ):
        """
        Args:
            collections:
                Initial items to store (list, set, single element, etc.).
            item_type (type | None):
                Optional type constraint for items.
            strict_type (bool):
                If True, items must match item_type exactly.
            progression (Progression | list[IDType] | None):
                If None, build from current dict keys. If a list, build a new
                `Progression`. If a `Progression` object, use it as-is.
            **kwargs:
                Additional args forwarded to `Element.__init__` (e.g. 'id').
        """
        super().__init__(**kwargs)
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()

        self.item_type = item_type
        self.strict_type = strict_type

        if collections is None:
            self.collections: dict[IDType, E] = {}
        else:
            self.collections = validate_collection_item_type(
                collections,
                item_type=self.item_type,
                strict_type=self.strict_type,
            )

        if progression is None:
            self.progression = Progression(order=list(self.collections.keys()))
        else:
            if isinstance(progression, Progression):
                self.progression = progression
            else:
                self.progression = Progression(order=progression)
            coll_ids = set(self.collections.keys())
            prog_ids = set(self.progression.order)
            if coll_ids != prog_ids:
                raise ValueError(
                    "Collections and progression must have the same items."
                )

    @property
    def lock(self) -> threading.Lock:
        """Synchronous lock for thread-safe operations."""
        return self._lock

    @property
    def async_lock(self) -> asyncio.Lock:
        """Async lock for thread-safe operations."""
        return self._async_lock

    def __len__(self) -> int:
        return len(self.collections)

    def __bool__(self) -> bool:
        return bool(self.collections)

    def __iter__(self) -> Iterator[E]:
        """Iterate items in progression order, synchronously."""
        with self.lock:
            current_order = list(self.progression)
        for oid in current_order:
            yield self.collections[oid]

    async def __aiter__(self) -> AsyncIterator[E]:
        """Iterate items in progression order, asynchronously."""
        async with self.async_lock:
            current_order = list(self.progression)
        for oid in current_order:
            yield self.collections[oid]
            await asyncio.sleep(0)

    def include(self, item: Any, /) -> bool:
        """
        Add items if not already present.
        Returns True if at least one new item was added, False otherwise.
        Does not raise errors for invalid or duplicate items.
        """
        try:
            item_dict = validate_collection_item_type(
                item, item_type=self.item_type, strict_type=self.strict_type
            )
        except (ValueError, TypeError):
            return False
        if not item_dict:
            return True

        # Filter out duplicates
        new_ids = [i for i in item_dict if i not in self.collections]
        if not new_ids:
            return False

        for i in new_ids:
            self.collections[i] = item_dict[i]
        added = self.progression.include(new_ids)
        return added

    def exclude(self, item: Any, /) -> bool:
        """
        Remove items if present.
        Returns True if any item was removed, False otherwise.
        Does not raise errors for missing or invalid items.
        """
        try:
            ids_to_remove = validate_order(item)
        except ValueError:
            return False
        if not ids_to_remove:
            return True

        remove_count = 0
        for oid in ids_to_remove:
            if oid in self.collections:
                del self.collections[oid]
                remove_count += 1
        ex = self.progression.exclude(ids_to_remove)
        return bool(remove_count) or ex

    @synchronized
    def append(self, item: Any) -> None:
        """
        Strictly append new items at the end.
        Raises ItemExistsError if any item already exists.
        """
        item_dict = validate_collection_item_type(
            item, item_type=self.item_type, strict_type=self.strict_type
        )
        for i in item_dict:
            if i in self.collections:
                raise ItemExistsError(f"Item {i} already exists.")
        self.collections.update(item_dict)
        self.progression.append(list(item_dict.keys()))

    @synchronized
    def remove(self, item: Any) -> None:
        """
        Strictly remove items, raising ItemNotFoundError if an item is missing.
        """
        ids_to_remove = validate_order(item)
        if not ids_to_remove:
            return
        missing = [i for i in ids_to_remove if i not in self.collections]
        if missing:
            raise ItemNotFoundError(f"Missing items: {missing}")

        for oid in ids_to_remove:
            del self.collections[oid]
        self.progression.exclude(ids_to_remove)

    @synchronized
    def insert(self, index: int, item: Any) -> None:
        """
        Strictly insert items at `index`, raising ItemExistsError if duplicates
        already exist.
        """
        item_dict = validate_collection_item_type(
            item, item_type=self.item_type, strict_type=self.strict_type
        )
        for i in item_dict:
            if i in self.collections:
                raise ItemExistsError(f"Item {i} already exists.")
        self.progression.insert(index, list(item_dict.keys()))
        self.collections.update(item_dict)

    @synchronized
    def pop(self, index: int = -1) -> E:
        """
        Pop an item by progression index (default last).
        Raises ItemNotFoundError if out of range.
        """
        try:
            popped_id = self.progression.pop(index)
        except Exception as e:
            raise ItemNotFoundError(str(e)) from e
        return self.collections.pop(popped_id)

    @synchronized
    def popleft(self) -> E:
        """Pop the first item in progression. Raises ItemNotFoundError if empty."""
        if not self.progression:
            raise ItemNotFoundError("Pile is empty.")
        popped_id = self.progression.popleft()
        return self.collections.pop(popped_id)

    def get(self, key: Any, default: Any = UNDEFINED) -> E | Any:
        """
        Retrieve an item by ID or return a default if not found.
        Does not raise an error for missing or invalid items.
        """
        from .element import ID

        try:
            oid = ID.get_id(key)
            return self.collections.get(oid, default)
        except:
            return default if default is not UNDEFINED else None

    @synchronized
    def clear(self) -> None:
        """Remove all items."""
        self.collections.clear()
        self.progression.clear()

    def __contains__(self, item: Any) -> bool:
        """Check if item(s) exist in the pile."""
        ids_ = []
        try:
            ids_ = validate_order(item)
        except:
            return False
        for oid in ids_:
            if oid not in self.collections:
                return False
        return True

    def to_list(self) -> list[E]:
        return [self.collections[k] for k in self.progression]

    def __list__(self) -> list[E]:
        return self.to_list()

    def to_df(
        self,
        *,
        columns: list[str] | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Convert items to a DataFrame, optionally specifying columns, etc.
        """
        data = [x.to_dict() for x in self]
        df = pd.DataFrame(data, columns=columns, **kwargs)
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(
                df["created_at"], errors="coerce"
            )
        return df

    def to_csv_file(self, path_or_buf: str | Path, **kwargs) -> None:
        """Save items as CSV."""
        df = self.to_df()
        df.to_csv(path_or_buf, index=False, **kwargs)
        logging.info(f"Saved Pile to {path_or_buf}")

    def to_json_file(
        self, path_or_buf: str | Path, indent: int = 2, **kwargs
    ) -> None:
        """Save items as JSON."""
        data = [item.to_dict() for item in self]
        with open(path_or_buf, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, **kwargs)
        logging.info(f"Saved Pile to {path_or_buf}")

    @classmethod
    def from_df(
        cls,
        df: pd.DataFrame,
        item_type: type[E] | None = None,
        strict_type: bool = False,
        **kwargs: Any,
    ) -> Self:
        """Construct a Pile from a DataFrame of items."""
        items = []
        for _, row in df.iterrows():
            if item_type:
                obj = item_type.from_dict(row.to_dict())
            else:
                obj = Element.from_dict(row.to_dict())
            items.append(obj)
        return cls(
            collections=items,
            item_type=item_type,
            strict_type=strict_type,
            **kwargs,
        )

    def adapt_to(
        self,
        obj_key: str,
        *,
        many: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Convert this Pile to another format using an adapter."""
        return self._get_adapter_registry().adapt_to(
            self, obj_key, many=many, **kwargs
        )

    @classmethod
    def adapt_from(
        cls,
        obj: Any,
        obj_key: str,
        *,
        many: bool = True,
        item_type: type[E] | None = None,
        strict_type: bool = False,
        **kwargs: Any,
    ) -> Self:
        """Construct a Pile from external data via an adapter."""
        data = cls._get_adapter_registry().adapt_from(
            cls, obj, obj_key, many=many, **kwargs
        )
        if isinstance(data, list):
            items = []
            for d in data:
                if isinstance(d, dict):
                    if item_type:
                        it = item_type.from_dict(d)
                    else:
                        it = Element.from_dict(d)
                    items.append(it)
                else:
                    items.append(d)
            return cls(
                collections=items, item_type=item_type, strict_type=strict_type
            )
        if isinstance(data, dict):
            # If 'collections' is present, parse it
            if "collections" in data:
                raw = data["collections"]
                parsed = []
                for r in raw:
                    if isinstance(r, dict):
                        if item_type:
                            it = item_type.from_dict(r)
                        else:
                            it = Element.from_dict(r)
                        parsed.append(it)
                    else:
                        parsed.append(r)
                data["collections"] = parsed
            return cls(item_type=item_type, strict_type=strict_type, **data)
        raise ValueError("Invalid data format from adapter.")

    def __next__(self) -> E:
        """Allow iteration via `next()`."""
        try:
            return next(iter(self))
        except StopIteration:
            raise StopIteration("End of pile")

    def __repr__(self) -> str:
        """Minimal representation of the pile."""
        size = len(self)
        if size == 0:
            return "Pile()"
        if size == 1:
            single = next(iter(self))
            return f"Pile({single})"
        return f"Pile(size={size})"

    __str__ = __repr__

    def to_dict(self) -> dict:
        dict_ = super().to_dict()
        dict_["collections"] = [x.to_dict() for x in self]
        dict_["progression"] = self.progression.to_dict()
        if self.item_type:
            dict_["item_type"] = self.item_type.class_name()
        if self.strict_type:
            dict_["strict_type"] = self.strict_type
        return dict_

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:
        strict_type = dict_.pop("strict_type", False)
        item_type = dict_.pop("item_type", None)
        if item_type:
            item_type = get_class(item_type)

        collections = dict_.pop("collections", [])
        progression = dict_.pop("progression", {})
        items = []
        for c in collections:
            items.append(Element.from_dict(c))
        prog = Progression.from_dict(progression)
        return cls(
            collections=items,
            item_type=item_type,
            strict_type=strict_type,
            progression=prog,
            **dict_,
        )

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


def pile(
    *,
    collections: Any = None,
    fp: str | Path | None = None,
    df: pd.DataFrame | None = None,
    item_type: type | None = None,
    strict_type: bool = False,
    progression: Progression | None = None,
    **kwargs: Any,
) -> Pile:
    """
    Convenience function to create a Pile from multiple sources:
      - `collections`: direct items
      - `fp`: file path (CSV or JSON)
      - `df`: DataFrame
      - optional `item_type`, `strict_type`, `progression`
    """
    if fp:
        p = Path(fp)
        suffix = p.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(p)
            return Pile.from_df(
                df, item_type=item_type, strict_type=strict_type, **kwargs
            )
        if suffix in (".json", ".jsonl"):
            return Pile.adapt_from(
                p,
                ".json",
                item_type=item_type,
                strict_type=strict_type,
                **kwargs,
            )
        raise ValueError(f"Unsupported file extension: {suffix}")

    if df is not None:
        return Pile.from_df(
            df, item_type=item_type, strict_type=strict_type, **kwargs
        )

    return Pile(
        collections=collections,
        item_type=item_type,
        strict_type=strict_type,
        progression=progression,
        **kwargs,
    )


# File: protocols/generic/pile.py
