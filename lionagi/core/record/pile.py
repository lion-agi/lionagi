"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
This module defines the Pile class, a versatile container for managing
collections of Element objects. It supports structured access and
manipulation, including retrieval, addition, and deletion of elements.
"""

from collections.abc import Iterable
from typing import TypeVar, Type, Any, Generic
from pydantic import Field, field_validator
from lionagi.os.lib import to_df
from ...lionagi.collections.model.imodel import iModel
from ...lionagi.collections.util import is_same_dtype, to_list_type, _validate_order

from ..abc import (
    Element,
    Record,
    Component,
    Ordering,
    LionIDable,
    get_lion_id,
    LionValueError,
    LionTypeError,
    ItemNotFoundError,
)

from ..primitives._mixin.embed_mixin import PileEmbeddingsMixin
from ..primitives._mixin.query_mixin import PileQueryMixin


T = TypeVar("T")


class Pile(Element, PileEmbeddingsMixin, PileQueryMixin, Record, Generic[T]):
    """
    Collection class for managing Element objects.

    Facilitates ordered and type-validated storage and access, supporting
    both index-based and key-based retrieval.

    Attributes:
        pile (dict[str, T]): Maps unique identifiers to items.
        item_type (set[Type[Element]] | None): Allowed item types.
        name (str | None): Optional name for the pile.
        order (list[str]): Order of item identifiers.
        use_obj (bool): If True, treat Record and Ordering as objects.
    """

    use_obj: bool = False
    pile: dict[str, T] = Field(default_factory=dict)
    item_type: set[Type[Element]] | None = Field(default=None)
    name: str | None = None
    order: list[str] = Field(default_factory=list)
    index: Any = None
    engines: dict[str, Any] = Field(default_factory=dict)
    query_response: list = []
    tools: dict = {}

    def __init__(
        self,
        items=None,
        item_type=None,
        order=None,
        use_obj=None,
    ):
        super().__init__()

        self.use_obj = use_obj or False
        self.pile = self._validate_pile(items or {})
        self.item_type = self._validate_item_type(item_type)

        order = order or list(self.pile.keys())
        if not len(order) == len(self):
            raise ValueError(
                "The length of the order does not match the length of the pile"
            )
        self.order = order

    def __getitem__(self, key) -> T | "Pile[T]":
        """
        Retrieve items from the pile using a key.

        Supports multiple types of key access:
        - By index or slice (list-like access)
        - By LionID (dictionary-like access)
        - By other complex types if item is of LionIDable

        Args:
            key: Key to retrieve items.

        Returns:
            The requested item(s). Single items returned directly,
            multiple items returned in a new `Pile` instance.

        Raises:
            ItemNotFoundError: If requested item(s) not found.
            LionTypeError: If provided key is invalid.
        """
        try:
            if isinstance(key, (int, slice)):
                # Handle list-like index or slice
                _key = self.order[key]
                _key = [_key] if isinstance(key, int) else _key
                _out = [self.pile.get(i) for i in _key]
                return _out[0] if len(_out) == 1 else pile(_out, self.item_type, _key)
        except IndexError as e:
            raise ItemNotFoundError(key) from e

        keys = to_list_type(key)
        for idx, item in enumerate(keys):
            if isinstance(item, str):
                keys[idx] = item
                continue
            if hasattr(item, "ln_id"):
                keys[idx] = item.ln_id

        if not all(keys):
            raise LionTypeError("Invalid item type. Expected LionIDable object(s).")

        try:
            if len(keys) == 1:
                return self.pile.get(keys[0])
            return pile([self.pile.get(i) for i in keys], self.item_type, keys)
        except KeyError as e:
            raise ItemNotFoundError(key) from e

    def __setitem__(self, key, item) -> None:
        """
        Set new values in the pile using various key types.

        Handles single/multiple assignments, ensures type consistency.
        Supports index/slice, LionID, and LionIDable key access.

        Args:
            key: Key to set items. Can be index, slice, LionID, LionIDable.
            item: Item(s) to set. Can be single item or collection.

        Raises:
            ValueError: Length mismatch or multiple items to single key.
            LionTypeError: Item type doesn't match allowed types.
        """
        item = self._validate_pile(item)

        if isinstance(key, (int, slice)):
            # Handle list-like index or slice
            try:
                _key = self.order[key]
            except IndexError as e:
                raise e

            if isinstance(_key, str) and len(item) != 1:
                raise ValueError("Cannot assign multiple items to a single item.")

            if isinstance(_key, list) and len(item) != len(_key):
                raise ValueError(
                    "The length of values does not match the length of the slice"
                )

            for k, v in item.items():
                if self.item_type and type(v) not in self.item_type:
                    raise LionTypeError(f"Invalid item type. Expected {self.item_type}")

                self.pile[k] = v
                self.order[key] = k
                self.pile.pop(_key)
            return

        if len(to_list_type(key)) != len(item):
            raise ValueError("The length of keys does not match the length of values")

        self.pile.update(item)
        self.order.extend(item.keys())

    def __contains__(self, item: Any) -> bool:
        """
        Check if item(s) are present in the pile.

        Accepts individual items and collections. Returns `True` if all
        provided items are found, `False` otherwise.

        Args:
            item: Item(s) to check. Can be single item or collection.

        Returns:
            `True` if all items are found, `False` otherwise.
        """
        item = to_list_type(item)
        for i in item:
            try:
                a = i if isinstance(i, str) else get_lion_id(i)
                if a not in self.pile:
                    return False
            except Exception:
                return False

        return True

    def pop(self, key: Any, default=...) -> T | "Pile[T]" | None:
        """
        Remove and return item(s) associated with given key.

        Raises `ItemNotFoundError` if key not found and no default given.
        Returns default if provided and key not found.

        Args:
            key: Key of item(s) to remove and return. Can be single key
                or collection of keys.
            default: Default value if key not found. If not specified
                and key not found, raises `ItemNotFoundError`.

        Returns:
            Removed item(s) associated with key. Single items returned
            directly, multiple items in new `Pile`. Returns default if
            provided and key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        key = to_list_type(key)
        items = []

        for i in key:
            if i not in self:
                if default == ...:
                    raise ItemNotFoundError(i)
                return default

        for i in key:
            _id = get_lion_id(i)
            items.append(self.pile.pop(_id))
            self.order.remove(_id)

        return pile(items) if len(items) > 1 else items[0]

    def get(self, key: Any, default=...) -> T | "Pile[T]" | None:
        """
        Retrieve item(s) associated with given key.

        Raises `ItemNotFoundError` if key not found and no default given.
        Returns default if provided and key not found.

        Args:
            key: Key of item(s) to retrieve. Can be single or collection.
            default: Default value if key not found. If not specified
                and key not found, raises `ItemNotFoundError`.

        Returns:
            Retrieved item(s) associated with key. Single items returned
            directly, multiple items in new `Pile`. Returns default if
            provided and key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        try:
            return self[key]
        except ItemNotFoundError as e:
            if default == ...:
                raise e
            return default

    def update(self, other: Any):
        """
        Update pile with another collection of items.

        Accepts `Pile` or any iterable. Provided items added to current
        pile, overwriting existing items with same keys.

        Args:
            other: Collection to update with. Can be any LionIDable
        """
        p = pile(other)
        self[p] = p

    def clear(self):
        """Clear all items, resetting pile to empty state."""
        self.pile.clear()
        self.order.clear()

    def include(self, item: Any) -> bool:
        """
        Include item(s) in pile if not already present.

        Accepts individual items and collections. Adds items if not
        present. Returns `True` if item(s) in pile after operation,
        `False` otherwise.

        Args:
            item: Item(s) to include. Can be single item or collection.

        Returns:
            `True` if item(s) in pile after operation, `False` otherwise.
        """
        item = to_list_type(item)
        if item not in self:
            self[item] = item
        return item in self

    def exclude(self, item: Any) -> bool:
        """
        Exclude item(s) from pile if present.

        Accepts individual items and collections. Removes items if
        present. Returns `True` if item(s) not in pile after operation,
        `False` otherwise.

        Args:
            item: Item(s) to exclude. Can be single item or collection.

        Returns:
            `True` if item(s) not in pile after operation, `False` else.
        """
        item = to_list_type(item)
        for i in item:
            if item in self:
                self.pop(i)
        return item not in self

    def is_homogenous(self) -> bool:
        """
        Check if all items have the same data type.

        Returns:
            `True` if all items have the same type, `False` otherwise.
            Empty pile or single-item pile considered homogenous.
        """
        return len(self.pile) < 2 or all(is_same_dtype(self.pile.values()))

    def is_empty(self) -> bool:
        """
        Check if the pile is empty.

        Returns:
            bool: `True` if the pile is empty, `False` otherwise.
        """
        return not self.pile

    def __iter__(self):
        """Return an iterator over the items in the pile.

        Yields:
            The items in the pile in the order they were added.
        """
        return iter(self.values())

    def __len__(self) -> int:
        """Get the number of items in the pile.

        Returns:
            int: The number of items in the pile.
        """
        return len(self.pile)

    def __add__(self, other: T) -> "Pile":
        """Create a new pile by including item(s) using `+`.

        Returns a new `Pile` with all items from the current pile plus
        provided item(s). Raises `LionValueError` if item(s) can't be
        included.

        Args:
            other: Item(s) to include. Can be single item or collection.

        Returns:
            New `Pile` with all items from current pile plus item(s).

        Raises:
            LionValueError: If item(s) can't be included.
        """
        _copy = self.model_copy(deep=True)
        if _copy.include(other):
            return _copy
        raise LionValueError("Item cannot be included in the pile.")

    def __sub__(self, other) -> "Pile":
        """
        Create a new pile by excluding item(s) using `-`.

        Returns a new `Pile` with all items from the current pile except
        provided item(s). Raises `ItemNotFoundError` if item(s) not found.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            New `Pile` with all items from current pile except item(s).

        Raises:
            ItemNotFoundError: If item(s) not found in pile.
        """
        _copy = self.model_copy(deep=True)
        if other not in self:
            raise ItemNotFoundError(other)

        length = len(_copy)
        if not _copy.exclude(other) or len(_copy) == length:
            raise LionValueError("Item cannot be excluded from the pile.")
        return _copy

    def __iadd__(self, other: T) -> "Pile":
        """
        Include item(s) in the current pile in place using `+=`.

        Modifies the current pile in-place by including item(s). Returns
        the modified pile.

        Args:
            other: Item(s) to include. Can be single item or collection.
        """

        return self + other

    def __isub__(self, other: LionIDable) -> "Pile":
        """
        Exclude item(s) from the current pile using `-=`.

        Modifies the current pile in-place by excluding item(s). Returns
        the modified pile.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            Modified pile after excluding item(s).
        """
        return self - other

    def __radd__(self, other: T) -> "Pile":
        return other + self

    def size(self) -> int:
        """Return the total size of the pile."""
        return sum([len(i) for i in self])

    def insert(self, index, item):
        """
        Insert item(s) at specific position.

        Inserts item(s) at specified index. Index must be integer.
        Raises `IndexError` if index out of range.

        Args:
            index: Index to insert item(s). Must be integer.
            item: Item(s) to insert. Can be single item or collection.

        Raises:
            ValueError: If index not an integer.
            IndexError: If index out of range.
        """
        if not isinstance(index, int):
            raise ValueError("Index must be an integer for pile insertion.")
        item = self._validate_pile(item)
        for k, v in item.items():
            self.order.insert(index, k)
            self.pile[k] = v

    def append(self, item: T):
        """
        Append item to end of pile.

        Appends item to end of pile. If item is `Pile`, added as single
        item, preserving structure. Only way to add `Pile` into another.
        Other methods assume pile as container only.

        Args:
            item: Item to append. Can be any object, including `Pile`.
        """
        self.pile[item.ln_id] = item
        self.order.append(item.ln_id)

    def keys(self):
        """Yield the keys of the items in the pile."""
        return self.order

    def values(self):
        """Yield the values of the items in the pile."""
        yield from (self.pile.get(i) for i in self.order)

    def items(self):
        """
        Yield the items in the pile as (key, value) pairs.

        Yields:
            tuple: A tuple containing the key and value of each item in the pile.
        """
        yield from ((i, self.pile.get(i)) for i in self.order)

    @field_validator("order", mode="before")
    def _validate_order(cls, value):
        return _validate_order(value)

    def _validate_item_type(self, value):
        """
        Validate the item type for the pile.

        Ensures that the provided item type is a subclass of Element or iModel.
        Raises an error if the validation fails.

        Args:
            value: The item type to validate. Can be a single type or a list of types.

        Returns:
            set: A set of validated item types.

        Raises:
            LionTypeError: If an invalid item type is provided.
            LionValueError: If duplicate item types are detected.
        """
        if value is None:
            return None

        value = to_list_type(value)

        for i in value:
            if not isinstance(i, (type(Element), type(iModel))):
                raise LionTypeError(
                    "Invalid item type. Expected a subclass of Component."
                )

        if len(value) != len(set(value)):
            raise LionValueError("Detected duplicated item types in item_type.")

        if len(value) > 0:
            return set(value)

    def _validate_pile(
        self,
        value,
    ):
        if value == {}:
            return value

        if isinstance(value, Component):
            return {value.ln_id: value}

        if self.use_obj:
            if not isinstance(value, list):
                value = [value]
            if isinstance(value[0], (Record, Ordering)):
                return {getattr(i, "ln_id"): i for i in value}

        value = to_list_type(value)
        if getattr(self, "item_type", None) is not None:
            for i in value:
                if not type(i) in self.item_type:
                    raise LionTypeError(
                        f"Invalid item type in pile. Expected {self.item_type}"
                    )

        if isinstance(value, list):
            if len(value) == 1:
                if isinstance(value[0], dict) and value[0] != {}:
                    k = list(value[0].keys())[0]
                    v = value[0][k]
                    return {k: v}

                # [item]
                k = getattr(value[0], "ln_id", None)
                if k:
                    return {k: value[0]}

            return {i.ln_id: i for i in value}

        raise LionValueError("Invalid pile value")

    def to_df(self):
        """Return the pile as a DataFrame."""
        dicts_ = []
        for i in self.values():
            _dict = i.to_dict()
            if _dict.get("embedding", None):
                _dict["embedding"] = str(_dict.get("embedding"))
            dicts_.append(_dict)
        return to_df(dicts_)

    def to_csv(self, file_name, **kwargs):
        """
        Save the pile to a CSV file.

        Args:
            file_name (str): The name of the CSV file.
            **kwargs: Additional keyword arguments for the CSV writer.
        """
        self.to_df().to_csv(file_name, index=False, **kwargs)

    @classmethod
    def from_csv(cls, file_name, **kwargs):
        """
        Load a pile from a CSV file.

        Args:
            file_name (str): The name of the CSV file.
            **kwargs: Additional keyword arguments for the CSV reader.

        Returns:
            Pile: The loaded pile.
        """
        from pandas import read_csv

        df = read_csv(file_name, **kwargs)
        items = Component.from_obj(df)
        return cls(items)

    @classmethod
    def from_df(cls, df):
        """
        Load a pile from a DataFrame.

        Args:
            df (DataFrame): The DataFrame to load.

        Returns:
            Pile: The loaded pile.
        """
        items = Component.from_obj(df)
        return cls(items)

    def __list__(self):
        """
        Get a list of the items in the pile.

        Returns:
            list: The items in the pile.
        """
        return list(self.pile.values())

    def __str__(self):
        """
        Get the string representation of the pile.

        Returns:
            str: The string representation of the pile.
        """
        return self.to_df().__str__()

    def __repr__(self):
        """
        Get the representation of the pile.

        Returns:
            str: The representation of the pile.
        """
        return self.to_df().__repr__()


def pile(
    items: Iterable[T] | None = None,
    item_type: set[Type] | None = None,
    order=None,
    use_obj=None,
    csv_file=None,
    df=None,
    **kwargs,
) -> Pile[T]:
    """
    Create a new Pile instance.

    This function provides various ways to create a Pile instance:
    - Directly from items
    - From a CSV file
    - From a DataFrame

    Args:
        items (Iterable[T] | None): The items to include in the pile.
        item_type (set[Type] | None): The allowed types of items in the pile.
        order (list[str] | None): The order of items.
        use_obj (bool | None): Whether to treat Record and Ordering as objects.
        csv_file (str | None): The path to a CSV file to load items from.
        df (DataFrame | None): A DataFrame to load items from.
        **kwargs: Additional keyword arguments for loading from CSV or DataFrame.

    Returns:
        Pile[T]: A new Pile instance.

    Raises:
        ValueError: If invalid arguments are provided.
    """
    if csv_file:
        return Pile.from_csv(csv_file, **kwargs)
    if df:
        return Pile.from_df(df)

    return Pile(items, item_type, order, use_obj)
