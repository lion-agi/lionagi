from __future__ import annotations

import asyncio
import threading
from collections.abc import (
    AsyncIterator,
    Callable,
    Iterable,
    Iterator,
    Sequence,
)
from functools import wraps
from typing import Any, ClassVar, Generic, TypeVar

from lionabc import Collective, Observable
from lionabc.exceptions import (
    ItemExistsError,
    ItemNotFoundError,
    LionTypeError,
    LionValueError,
)
from lionfuncs import LN_UNDEFINED, is_same_dtype, to_list
from pydantic import Field, field_serializer
from typing_extensions import Self, override

from lion_core.generic.element import Element
from lion_core.generic.progression import Progression
from lion_core.generic.utils import to_list_type, validate_order
from lion_core.protocols.adapter import Adapter, AdapterRegistry
from lion_core.sys_utils import SysUtil

T = TypeVar("T", bound=Observable)


def synchronized(func: Callable):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)

    return wrapper


def async_synchronized(func: Callable):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self.async_lock:
            return await func(self, *args, **kwargs)

    return wrapper


PILE_KEY_TYPE = int | str | slice


class Pile(Element, Collective, Generic[T]):
    """
    thread-safe async-compatible, ordered collection of Observable elements.

    Pile is a core container in the Lion framework for managing collections
    of Observable objects. It maintains item order and allows fast access
    by unique identifiers, combining list and dictionary characteristics.

    Key Features:
        - Ordered storage with fast access (O(1) by index or Lion ID)
        - Optional type enforcement
        - Thread-safe write operations
        - Asynchronous support for key operations
        - Flexible synchronous and asynchronous iteration

    Thread Safety:
        - State-modifying methods are thread-safe
        - Read-only methods are not synchronized for performance
        - Caution advised when iterating during modifications

    Asynchronous Support:
        - Async versions of state-modifying methods (prefixed with 'a')
        - Asynchronous iteration via __aiter__
        - Read-only methods safe in async contexts without 'await'

    Args:
        items: Initial items for the pile. Defaults to None.
        item_type: Allowed types for items. Defaults to None (any Observable).
        order: Initial order of items. Defaults to None.
        strict: If True, enforces strict type checking. Defaults to False.

    Attributes:
        pile (dict[str, T]): Internal storage mapping Lion IDs to items.
        item_type (set[Type[Observable]] | None): Set of allowed item types.
        order (Progression): Maintains the order of items.
        strict (bool): Whether to enforce strict type checking.

    Example:
        >>> from lion_core.generic.pile import Pile
        >>> from lionabc import Observable
        >>>
        >>> class MyItem(Observable):
        ...     def __init__(self, value):
        ...         super().__init__()
        ...         self.value = value
        >>>
        >>> # Create a Pile
        >>> my_pile = Pile(items=[MyItem(1), MyItem(2)], item_type={MyItem})
        >>>
        >>> # Add items
        >>> my_pile.include(MyItem(3))
        >>>
        >>> # Access items
        >>> item = my_pile[0]  # By index
        >>> print(item.value)
        1
        >>>
        >>> # Iterate
        >>> for item in my_pile:
        ...     print(item.value)
        1
        2
        3
        >>>
        >>> # Remove items
        >>> removed_item = my_pile.pop(0)
        >>> print(removed_item.value)
        1

    Notes:
        - Maintains a snapshot view during iteration to prevent concurrent
          modification issues.
        - When subclassing, use @synchronized and @async_synchronized
          decorators for methods that modify state to maintain thread-safety.
        - Not safe for concurrent writes from multiple threads or asyncio
          tasks without external synchronization.

    Warning:
        Modifying the Pile during iteration may lead to unexpected behavior.
        Use the iteration snapshot for safe concurrent access.
    """

    pile_: dict[str, T] = Field(default_factory=dict)
    item_type: set[type[Observable]] | None = Field(
        default=None,
        description="Set of allowed types for items in the pile.",
        exclude=True,
    )
    order: Progression = Field(
        default_factory=Progression,
        description="Progression specifying the order of items in the pile.",
        exclude=True,
    )
    strict_type: bool = Field(
        default=False,
        description="Specify if enforce a strict type check",
        frozen=True,
    )

    _adapter_registry: ClassVar[AdapterRegistry] = AdapterRegistry

    def __pydantic_extra__(self) -> dict[str, Any]:
        return {
            "_lock": Field(default_factory=threading.Lock),
            "_async": Field(default_factory=asyncio.Lock),
        }

    def __pydantic_private__(self) -> dict[str, Any]:
        return self.__pydantic_extra__()

    @override
    def __init__(
        self,
        items: Any = None,
        item_type: set[type[Observable]] | None = None,
        order: Progression | list | None = None,
        strict_type: bool = False,
        **kwargs,
    ) -> None:
        """
        Initialize a Pile instance.

        Args:
            items: Initial items for the pile.
            item_type: Allowed types for items in the pile.
            order: Initial order of items (as Progression).
            strict: If True, enforce strict type checking.
        """
        _config = {}
        if "ln_id" in kwargs:
            _config["ln_id"] = kwargs["ln_id"]
        if "created" in kwargs:
            _config["created"] = kwargs["created"]

        super().__init__(strict_type=strict_type, **_config)
        self.item_type = self._validate_item_type(item_type)
        self.pile_ = self._validate_pile(items or kwargs.get("pile_", {}))
        self.order = self._validate_order(order)

    # Sync Interface methods
    @override
    @classmethod
    def from_dict(
        cls: type[T],
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
        items = data.pop("pile_", [])
        items = [Element.from_dict(i) for i in items]
        return cls(items=items, **data)

    def __setitem__(self, key: PILE_KEY_TYPE, item: T | Sequence[T]) -> None:
        """Set an item or items in the Pile.

        Args:
            key: The key to set. Can be an integer index, a string ID, or a
                slice.
            item: The item or items to set. Must be of type T or a sequence
                of T for slices.

        Raises:
            TypeError: If the item type is not allowed.
            KeyError: If the key is invalid.
            ValueError: If trying to set multiple items with a non-slice key.
        """
        self._setitem(key, item)

    @synchronized
    def pop(
        self,
        key: PILE_KEY_TYPE,
        default: Any = LN_UNDEFINED,
        /,
    ) -> T | Pile | None:
        """Remove and return an item or items from the Pile.

        Args:
            key: The key of the item(s) to remove. Can be an integer index,
                a string ID, or a slice.
            default: The value to return if the key is not found. Defaults to
                LN_UNDEFINED.

        Returns:
            The removed item(s), or the default value if not found.

        Raises:
            KeyError: If the key is not found and no default is provided.
        """
        return self._pop(key, default)

    def remove(
        self,
        item: T,
        /,
    ) -> None:
        """Remove a specific item from the Pile.

        Args:
            item: The item to remove.

        Raises:
            ValueError: If the item is not found in the Pile.
        """
        self._remove(item)

    def include(
        self,
        item: T | Iterable[T],
        /,
    ) -> None:
        """Include item(s) in the Pile if not already present.

        Args:
            item: Item or iterable of items to include.

        Raises:
            TypeError: If the item(s) are not of allowed types.
        """
        self._include(item)

    def exclude(
        self,
        item: T | Iterable[T],
        /,
    ) -> None:
        """Exclude item(s) from the Pile if present.

        Args:
            item: Item or iterable of items to exclude.

        Note:
            This method does not raise an error if an item is not found.
        """
        self._exclude(item)

    @synchronized
    def clear(self) -> None:
        """Remove all items from the Pile."""
        self._clear()

    def update(
        self,
        other: Any,
        /,
    ) -> None:
        """Update Pile with items from another iterable or Pile.

        Args:
            other: An iterable or another Pile to update from.

        Raises:
            TypeError: If the items in 'other' are not of allowed types.
        """
        self._update(other)

    @synchronized
    def insert(self, index: int, item: T, /) -> None:
        """Insert an item at a specific position in the Pile.

        Args:
            index: The index at which to insert the item.
            item: The item to insert.

        Raises:
            IndexError: If the index is out of range.
            TypeError: If the item is not of an allowed type.
        """
        self._insert(index, item)

    @synchronized
    def append(self, item: T, /) -> None:
        """Append an item to the end of the Pile.

        This method is an alias for `include`.

        Args:
            item: The item to append.

        Raises:
            TypeError: If the item is not of an allowed type.
        """
        self.update(item)

    @synchronized
    def get(
        self,
        key: PILE_KEY_TYPE,
        default: Any = LN_UNDEFINED,
        /,
    ) -> T | Pile | None:
        """Retrieve item(s) associated with the given key.

        Args:
            key: The key of item(s) to retrieve. Can be an integer index,
                a string ID, or a slice.
            default: Value to return if the key is not found. Defaults to
                LN_UNDEFINED.

        Returns:
            The item(s) associated with the key, or the default value if not
            found. Returns a new Pile instance for slice keys.

        Note:
            Unlike `__getitem__`, this method does not raise KeyError for
            missing keys when a default is provided.
        """
        return self._get(key, default)

    def keys(self) -> Sequence[str]:
        """Return a sequence of all keys (Lion IDs) in the Pile.

        Returns:
            A sequence of string keys representing the Lion IDs of items
            in their current order.
        """
        return list(self.order)

    def values(self) -> Sequence[T]:
        """Return a sequence of all values in the Pile.

        Returns:
            A sequence of all items in the Pile in their current order.
        """
        return [self.pile_[key] for key in self.order]

    def items(self) -> Sequence[tuple[str, T]]:
        """Return a sequence of all (key, value) pairs in the Pile.

        Returns:
            A sequence of tuples, each containing a string key (Lion ID)
            and its corresponding item, in their current order.
        """
        return [(key, self.pile_[key]) for key in self.order]

    def is_empty(self) -> bool:
        """Check if the Pile is empty.

        Returns:
            True if the Pile contains no items, False otherwise.
        """

        return len(self.order) == 0

    def size(self) -> int:
        """Get the number of items in the Pile.

        Returns:
            The count of items currently in the Pile.

        Note:
            This method is equivalent to using the `len()` function
            on the Pile.
        """
        return len(self.order)

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over the items in the Pile.

        This method creates a snapshot of the current order to prevent
        issues with concurrent modifications during iteration.

        Yields:
            Items in the Pile in their current order.
        """
        with self.lock:
            current_order = list(self.order)

        for key in current_order:
            yield self.pile_[key]

    def __next__(self) -> T:
        """Return the next item in the Pile.

        Returns:
            The next item in the Pile.

        Raises:
            StopIteration: When there are no more items in the Pile.
        """
        try:
            return next(iter(self))
        except StopIteration:
            raise StopIteration("End of pile")

    def __getitem__(self, key: PILE_KEY_TYPE) -> Any | list | T:
        """Get item(s) from the Pile by index, ID, or slice.

        Args:
            key: Integer index, string ID, or slice.

        Returns:
            The item or a new Pile containing the sliced items.

        Raises:
            KeyError: If the key is not found.
            TypeError: If the key type is invalid.
        """
        return self._getitem(key)

    def __contains__(self, item: Any) -> bool:
        """Check if an item is in the Pile.

        Args:
            item: The item to check for.

        Returns:
            True if the item is in the Pile, False otherwise.
        """
        return item in self.order

    def __len__(self) -> int:
        """Return the number of items in the Pile.

        Returns:
            The number of items in the Pile.
        """
        return len(self.pile_)

    @override
    def __bool__(self) -> bool:
        """Check if the Pile is not empty.

        Returns:
            True if the Pile is not empty, False otherwise.
        """
        return not self.is_empty()

    def __list__(self) -> list[T]:
        """Convert the Pile to a list.

        Returns:
            A list containing all items in the Pile.
        """
        return self.values()

    def __ior__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )
        other = self._validate_pile(list(other))
        self.include(other)
        return self

    def __or__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        result = self.__class__(
            items=self.values(),
            item_type=self.item_type,
            order=self.order,
        )
        result.include(list(other))
        return result

    def __ixor__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        to_exclude = []
        for i in other:
            if i in self:
                to_exclude.append(i)

        other = [i for i in other if i not in to_exclude]
        self.exclude(to_exclude)
        self.include(other)
        return self

    def __xor__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
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

    def __iand__(self, other: Any | Self) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        to_exclude = []
        for i in self.values():
            if i not in other:
                to_exclude.append(i)
        self.exclude(to_exclude)
        return self

    def __and__(self, other: Any | Pile) -> Pile:
        if not isinstance(other, Pile):
            raise LionTypeError(
                "Invalid type for Pile operation.",
                expected_type=Pile,
                actual_type=type(other),
            )

        values = [i for i in self if i in other]
        return self.__class__(
            items=values,
            item_type=self.item_type,
        )

    @override
    def __str__(self) -> str:
        """Return a string representation of the Pile.

        Returns:
            A string in the format "Pile(length)".
        """
        return f"Pile({len(self)})"

    @override
    def __repr__(self) -> str:
        """Return a detailed string representation of the Pile.

        Returns:
            A string representation of the Pile, showing its contents
            for small Piles or just the length for larger ones.
        """
        length = len(self)
        if length == 0:
            return "Pile()"
        elif length == 1:
            return f"Pile({next(iter(self.pile_.values())).__repr__()})"
        else:
            return f"Pile({length})"

    def __getstate__(self):
        """Prepare the Pile instance for pickling."""
        state = self.__dict__.copy()
        state["_lock"] = None
        state["_async_lock"] = None
        return state

    def __setstate__(self, state):
        """Restore the Pile instance after unpickling."""
        self.__dict__.update(state)
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    @property
    def lock(self):
        """Ensure the lock is always available, even during unpickling."""
        if not hasattr(self, "_lock") or self._lock is None:
            self._lock = threading.Lock()
        return self._lock

    @property
    def async_lock(self):
        """Ensure the async lock is always available, even during unpickling"""
        if not hasattr(self, "_async_lock") or self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    # Async Interface methods
    @async_synchronized
    async def asetitem(
        self,
        key: PILE_KEY_TYPE,
        item: T | Iterable[T],
        /,
    ) -> None:
        """Asynchronously set an item or items in the Pile.

        Args:
            key: The key to set. Can be an integer index, a string ID, or a
                slice.
            item: The item or items to set. Must be of type T or an iterable
                of T for slices.

        Raises:
            TypeError: If the item type is not allowed.
            KeyError: If the key is invalid.
            ValueError: If trying to set multiple items with a non-slice key.
        """
        self._setitem(key, item)

    @async_synchronized
    async def apop(
        self,
        key: PILE_KEY_TYPE,
        default: Any = LN_UNDEFINED,
        /,
    ):
        """Asynchronously remove and return an item or items from the Pile.

        Args:
            key: The key of the item(s) to remove. Can be an integer index,
                a string ID, or a slice.
            default: The value to return if the key is not found. Defaults to
                LN_UNDEFINED.

        Returns:
            The removed item(s), or the default value if not found.

        Raises:
            KeyError: If the key is not found and no default is provided.
        """
        return self._pop(key, default)

    @async_synchronized
    async def aremove(
        self,
        item: T,
        /,
    ) -> None:
        """Asynchronously remove a specific item from the Pile.

        Args:
            item: The item to remove.

        Raises:
            ValueError: If the item is not found in the Pile.
        """
        self._remove(item)

    @async_synchronized
    async def ainclude(
        self,
        item: T | Iterable[T],
        /,
    ) -> None:
        """Asynchronously include item(s) in the Pile if not already present.

        Args:
            item: Item or iterable of items to include.

        Raises:
            TypeError: If the item(s) are not of allowed types.
        """
        self._include(item)
        if item not in self:
            raise LionTypeError(f"Item {item} is not of allowed types")

    @async_synchronized
    async def aexclude(
        self,
        item: T | Iterable[T],
        /,
    ) -> None:
        """Asynchronously exclude item(s) from the Pile if present.

        Args:
            item: Item or iterable of items to exclude.

        Note:
            This method does not raise an error if an item is not found.
        """
        self._exclude(item)

    @async_synchronized
    async def aclear(self) -> None:
        self._clear()

    @async_synchronized
    async def aupdate(
        self,
        other: Any,
        /,
    ) -> None:
        self._update(other)

    @async_synchronized
    async def aget(
        self,
        key: Any,
        default=LN_UNDEFINED,
        /,
    ) -> list | Any | T:
        return self._get(key, default)

    async def __aiter__(self) -> AsyncIterator[T]:
        """Return an asynchronous iterator over the items in the Pile.

        This method creates a snapshot of the current order to prevent
        issues with concurrent modifications during iteration.

        Yields:
            Items in the Pile in their current order.

        Note:
            This method yields control to the event loop after each item,
            allowing other async operations to run between iterations.
        """

        async with self.async_lock:
            current_order = list(self.order)

        for key in current_order:
            yield self.pile_[key]
            await asyncio.sleep(0)  # Yield control to the event loop

    async def __anext__(self) -> T:
        """Asynchronously return the next item in the Pile."""
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
                result_ids = self.order[key]
                result_ids = (
                    [result_ids]
                    if not isinstance(result_ids, list)
                    else result_ids
                )
                result = []
                for i in result_ids:
                    result.append(self.pile_[i])
                return result[0] if len(result) == 1 else result
            except Exception as e:
                raise ItemNotFoundError(f"index {key}. Error: {e}")

        elif isinstance(key, str):
            try:
                return self.pile_[key]
            except Exception as e:
                raise ItemNotFoundError(f"key {key}. Error: {e}")

        else:
            key = to_list_type(key)
            result = []
            try:
                for k in key:
                    result_id = SysUtil.get_id(k)
                    result.append(self.pile_[result_id])

                if len(result) == 0:
                    raise ItemNotFoundError(f"key {key} item not found")
                if len(result) == 1:
                    return result[0]
                return result
            except Exception as e:
                raise ItemNotFoundError(f"Key {key}. Error:{e}")

    def _setitem(self, key: Any, item: Any) -> None:
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
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i in self.order:
                raise ItemExistsError(f"item {i} already exists in the pile")
            item_order.append(i)
        if isinstance(key, int | slice):
            try:
                delete_order = (
                    list(self.order[key])
                    if isinstance(self.order[key], Progression)
                    else [self.order[key]]
                )
                self.order[key] = item_order
                for i in to_list(delete_order, flatten=True):
                    self.pile_.pop(i)
                self.pile_.update(item_dict)
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
                id_ = SysUtil.get_id(k)
                if id_ not in item_order:
                    raise KeyError(
                        f"Invalid key {id_}. Key and item does not match.",
                    )
            self.order += key
            self.pile_.update(item_dict)

    def _get(self, key: Any, default: Any = LN_UNDEFINED) -> list | Any | T:
        """
        Retrieve item(s) associated with given key.

        Args:
            key: Key of item(s) to retrieve. Can be single or collection.
            default: Default value if key not found.

        Returns:
            Retrieved item(s) or default if key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        if isinstance(key, int | slice):
            try:
                return self[key]
            except Exception as e:
                if default is LN_UNDEFINED:
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
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default

    def _pop(self, key: Any, default: Any = LN_UNDEFINED) -> list | Any | T:
        """
        Remove and return item(s) associated with given key.

        Args:
            key: Key of item(s) to remove. Can be single or collection.
            default: Default value if key not found.

        Returns:
            Removed item(s) or default if key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        if isinstance(key, int | slice):
            try:
                pops = self.order[key]
                pops = [pops] if isinstance(pops, str) else pops
                result = []
                for i in pops:
                    self.order.remove(i)
                    result.append(self.pile_.pop(i))
                result = (
                    self.__class__(items=result, item_type=self.item_type)
                    if len(result) > 1
                    else result[0]
                )
                return result
            except Exception as e:
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default
        else:
            try:
                key = validate_order(key)
                result = []
                for k in key:
                    self.order.remove(k)
                    result.append(self.pile_.pop(k))
                if len(result) == 0:
                    raise ItemNotFoundError(f"key {key} item not found")
                elif len(result) == 1:
                    return result[0]
                return result
            except Exception as e:
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default

    def _remove(self, item: T):
        """
        Remove an item from the pile.

        Args:
            item: The item to remove.

        Raises:
            ItemNotFoundError: If the item is not found in the pile.
        """
        if item in self:
            self.pop(item)
            return
        raise ItemNotFoundError(f"{item}")

    def _include(self, item: Any):
        """
        Include item(s) in pile if not already present.

        Args:
            item: Item(s) to include. Can be single item or collection.
        """
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i not in self.order:
                item_order.append(i)

        self.order.append(item_order)
        self.pile_.update(item_dict)

    def _exclude(self, item: Any):
        """
        Exclude item(s) from pile if present.

        Args:
            item: Item(s) to exclude. Can be single item or collection.
        """
        item = to_list_type(item)
        exclude_list = []
        for i in item:
            if i in self:
                exclude_list.append(i)
        if exclude_list:
            self.pop(exclude_list)

    def _clear(self) -> None:
        """Remove all items from the pile."""
        self.pile_.clear()
        self.order.clear()

    def _update(self, other: Any):
        """Update pile with another collection of items."""
        self.include(other)

    def _validate_item_type(self, value: Any) -> set[type[Observable]] | None:
        """
        Validate the item type for the pile.

        Ensures that the provided item type is a subclass of Element or iModel.
        Raises an error if the validation fails.

        Args:
            value: The item type to validate. Can be a single type or a list of
                    types.

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
            if not issubclass(i, Observable):
                raise LionTypeError(
                    message="Item type must be a subclass of Observable.",
                    expected_type=Observable,
                    actual_type=type(i),
                )

        if len(value) != len(set(value)):
            raise LionValueError(
                "Detected duplicated item types in item_type.",
            )

        if len(value) > 0:
            return set(value)

    def _validate_pile(self, value: Any) -> dict[str, T]:
        """Validate and convert the items to be added to the pile."""
        if not value:
            return {}

        value = to_list_type(value)

        result = {}
        for i in value:
            if self.item_type:
                if self.strict_type:
                    if type(i) not in self.item_type:
                        raise LionTypeError(
                            message="Invalid item type in pile."
                            f" Expected {self.item_type}",
                        )
                else:
                    if not any(issubclass(type(i), t) for t in self.item_type):
                        raise LionTypeError(
                            "Invalid item type in pile. Expected "
                            f"{self.item_type} or the subclasses",
                        )
            else:
                if not isinstance(i, Observable):
                    raise LionValueError(f"Invalid pile item {i}")

            result[i.ln_id] = i

        return result

    def _validate_order(self, value: Any) -> Progression:
        if not value:
            return self.order.__class__(order=list(self.pile_.keys()))

        if isinstance(value, Progression):
            value = list(value)
        else:
            value = to_list_type(value)

        value_set = set(value)
        if len(value_set) != len(value):
            raise LionValueError("There are duplicate elements in the order")
        if len(value_set) != len(self.pile_.keys()):
            raise LionValueError(
                "The length of the order does not match the length of the pile"
            )

        for i in value_set:
            if SysUtil.get_id(i) not in self.pile_.keys():
                raise LionValueError(
                    f"The order does not match the pile. {i} not found"
                )

        return self.order.__class__(order=value)

    def _append(self, item: T):
        """
        Append item to end of pile.

        Args:
            item: Item to append. Can be any lion object, including `Pile`.
        """
        self.update(item)

    def _insert(self, index: int, item: T):
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i in self.order:
                raise ItemExistsError(f"item {i} already exists in the pile")
            item_order.append(i)
        self.order.insert(index, item_order)
        self.pile_.update(item_dict)

    @field_serializer("pile_")
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
            item = self.pile[self.pile.order[self.index]]
            self.index += 1
            await asyncio.sleep(0)  # Yield control to the event loop
            return item

    def is_homogenous(self) -> bool:
        return len(self.pile_) < 2 or all(is_same_dtype(self.pile_.values()))

    def adapt_to(self, obj_key: str, /, **kwargs: Any) -> Any:
        return self._get_adapter_registry().adapt_to(self, obj_key, **kwargs)

    @classmethod
    def list_adapters(cls):
        return cls._get_adapter_registry().list_adapters()

    @classmethod
    def register_adapter(cls, adapter: type[Adapter]):
        cls._get_adapter_registry().register(adapter)

    @classmethod
    def _get_adapter_registry(cls) -> AdapterRegistry:
        """Get the converter registry for the class."""
        if isinstance(cls._adapter_registry, type):
            cls._adapter_registry = cls._adapter_registry()
        return cls._adapter_registry

    @classmethod
    def adapt_from(cls, obj: Any, obj_key: str, /, **kwargs: Any):
        dict_ = cls._get_adapter_registry().adapt_from(obj, obj_key, **kwargs)
        return cls.from_dict(dict_)


def pile(
    items: Any = None,
    /,
    item_type: type[Observable] | set[type[Observable]] | None = None,
    order: list[str] | None = None,
    strict_type: bool = False,
    **kwargs,
) -> Pile:
    """
    Create a new Pile instance.

    Args:
        items: Initial items for the pile.
        item_type: Allowed types for items in the pile.
        order: Initial order of items.
        strict: If True, enforce strict type checking.

    Returns:
        Pile: A new Pile instance.
    """

    return Pile(
        items,
        item_type=item_type,
        order=order,
        strict=strict_type,
        **kwargs,
    )


__all__ = [Pile, Pile]
# File: lion_core/generic/pile.py
