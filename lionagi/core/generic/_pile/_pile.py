from collections.abc import Iterable
from typing import TypeVar, Type, Any, Generic

from pydantic import Field, field_validator

from lionagi.libs.ln_convert import is_same_dtype, to_df
from ..abc import Record, Component, LionIDable, get_lion_id
from ..abc._exceptions import LionValueError, LionTypeError, ItemNotFoundError
from .._util import _to_list_type, _validate_order

# Define a type variable for components bound to the Component type
T = TypeVar("T", bound=Component)


class Pile(Component, Record, Generic[T]):
    """A collection of unique LionAGI items."""

    pile: dict[str, T] = Field(default_factory=dict)
    item_type: set[Type[Component]] | None = Field(default=None)
    name: str | None = None
    order: list[str] = Field(default_factory=list)

    def __getitem__(self, key) -> T | "Pile[T]":
        """
        Retrieve items using a key. Supports multiple types of key access:
        - By index or slice (list-like).
        - By LionID (dictionary-like).
        - Plus other complex types as long as the item is LionIDable.

        If a single object is requested, it returns the object;
        if multiple objects are requested, it returns a new pile of objects.
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

        keys = _to_list_type(key)

        if not all(keys):
            raise LionTypeError(
                "Invalid item type. Expected one or one collection of LionIDable object."
            )

        try:
            if len(keys) == 1:
                return self.pile.get(keys[0])
            return pile([self.pile.get(i) for i in keys], self.item_type, keys)
        except KeyError as e:
            raise ItemNotFoundError(key) from e

    def __setitem__(self, key, item) -> None:
        """
        Set new values in the pile using various key types.
        This method handles single or multiple assignments and ensures type consistency.
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

        if len(_to_list_type(key)) != len(item):
            raise ValueError("The length of keys does not match the length of values")

        self.pile.update(item)
        self.order.extend(item.keys())

    def __contains__(self, item: Any) -> bool:
        """
        Check if the item or items are present in the pile.
        This method accepts both individual items and collections of items.
        """
        item = _to_list_type(item)
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
        Remove and return the item(s) associated with key from the pile.
        If the key is not found and no default is specified, raises
        ItemNotFoundError.
        """
        key = _to_list_type(key)
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
        Retrieve the item associated with key. return default or raise
        ItemNotFoundError if not found.
        """
        try:
            return self[key]
        except ItemNotFoundError as e:
            if default == ...:
                raise e
            return default

    def update(self, other: Any):
        """
        Update the pile with another collection of items.
        This can include another pile or any iterable of items.
        """
        p = pile(self._validate_pile(other))
        self[p] = p

    def clear(self):
        """
        Clear all items from the pile, resetting it to an empty state.
        """
        self.pile.clear()
        self.order.clear()

    def include(self, item: Any) -> bool:
        """
        Include items in the pile if not already present.
        Returns True if the item is successfully included; otherwise, False.
        """
        item = _to_list_type(item)
        if item not in self:
            self[item] = item
        return item in self

    def exclude(self, item: Any) -> bool:
        """
        Exclude items from the pile if present.
        Returns True if the item is successfully excluded; otherwise, False.
        """ 
        item = _to_list_type(item)
        for i in item:
            if item in self:
                self.pop(i)
        return item not in self

    def is_homogenous(self) -> bool:
        """
        Check if all items in the pile have the same data type.
        Returns True if all items are of the same type. One item or an empty pile are considered homogenous.
        """
        return len(self.pile) < 2 or all(is_same_dtype(self.pile.values()))

    def is_empty(self) -> bool:
        """Determine if the pile is empty. True if the pile is empty; otherwise, False."""
        return not self.pile

    def __iter__(self):
        return iter(self.values())

    def __len__(self) -> int:
        """Return the number of items in the pile."""
        return len(self.pile)

    def __add__(self, other: T) -> "Pile":
        """
        Include to the pile using the + operator.
        Returns a new Pile instance containing all items from this pile plus the added item.
        Raises a LionValueError if the item cannot be included.
        """
        _copy = self.model_copy(deep=True)
        if _copy.include(other):
            return _copy
        raise LionValueError("Item cannot be included in the pile.")

    def __sub__(self, other):
        """
        Remove an item from the pile using the - operator.
        Returns a new Pile instance without the removed item.
        Raises an ItemNotFoundError if the item is not found in the pile.
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
        Add an item to the pile using the += operator.
        Modifies the pile in-place by including the specified item.
        Returns the modified pile.
        """
        return self + other

    def __isub__(self, other: LionIDable) -> "Pile":
        """
        Remove an item from the pile using the -= operator.
        Modifies the pile in-place by excluding the specified item.
        Returns the modified pile.
        """
        return self - other

    def __radd__(self, other: T) -> "Pile":
        return other + self

    def size(self):
        """Return the total size of the pile."""
        return sum([len(i) for i in self])

    def insert(self, index, item):
        if not isinstance(index, int):
            raise ValueError("Index must be an integer for pile insertion.")
        item = self._validate_pile(item)
        for k, v in item.items():
            self.order.insert(index, k)
            self.pile[k] = v

    def append(self, item: T):
        """
        Append an item to the pile.
        This is the only way to add a pile into another pile.
        all other methods assume pile as a container only
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
        yield from ((i, self.pile.get(i)) for i in self.order)

    @field_validator("order", mode="before")
    def _validate_order(cls, value):
        return _validate_order(value)        
        
    @field_validator("item_type", mode="before")
    def _validate_item_type(cls, value):
        """
        Validate the item_type field to ensure all types are subclasses of Component.
        Also checks for duplicates in the specified types.
        """
        """Validate the item_type field."""
        if value is None:
            return None

        value = _to_list_type(value)

        for i in value:
            if not isinstance(i, type(Component)):
                raise LionTypeError(
                    "Invalid item type. Expected a subclass of Component."
                )

        if len(value) != len(set(value)):
            raise LionValueError("Detected duplicated item types in item_type.")

        if len(value) > 0:
            return set(value)

    @field_validator("pile", mode="before")
    def _validate_pile(
        cls,
        value,
    ):
        """
        Validate the pile before updating or setting it.
        Ensures all elements are of allowed types and are unique based on their LionID.
        """
        if isinstance(value, Component):
            return {value.ln_id: value}

        value = _to_list_type(value)
        if getattr(cls, "item_type", None) is not None:
            for i in value:
                if not type(i) in cls.item_type:
                    raise LionTypeError(
                        f"Invalid item type in pile. Expected {cls.item_type}"
                    )

        if isinstance(value, list):
            if len(value) == 1:
                return {value[0].ln_id: value[0]}
            return {i.ln_id: i for i in value}

        raise LionValueError("Invalid pile value")

    def to_df(self):
        """Return the pile as a DataFrame."""
        dicts_ = []
        for i in self.values():
            _dict = i.to_dict()
            dicts_.append(_dict)
        return to_df(dicts_)

    def __list__(self):
        return list(self.pile.values())

    def __str__(self):
        return self.to_df().__str__()

    def __repr__(self):
        return self.to_df().__repr__()


def pile(
    items: Iterable[T] | None = None, item_type: set[Type] | None = None, order=None,
) -> Pile[T]:
    """Create a new Pile instance."""
    if not items:
        return Pile(item_type=item_type) if item_type else Pile()

    a = Pile(pile=items, item_type=item_type)
    order = order or list(a.pile.keys())
    if not len(order) == len(a):
        raise ValueError("The length of the order does not match the length of the pile")
    
    a.order = order
    return a
