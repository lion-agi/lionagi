from collections.abc import Iterable
from typing import TypeVar, Type, Any, Generic
from pydantic import Field, field_validator

from lionagi.libs.ln_convert import is_same_dtype, to_df
from ..abc import Record, Component, LionIDable, get_lion_id
from .._util import _to_list_type
from ..abc._exceptions import LionValueError, LionTypeError, ItemNotFoundError


T = TypeVar("T", bound=Component)

    
class Pile(Component, Record, Generic[T]):
    """A collection of unique LionAGI items."""

    pile: dict[str, T] = Field(default_factory=dict, alias="items")
    item_type: set[Type[Component]] | None = Field(default=None)
    name: str | None = None
    order: list[str] = Field(default_factory=list)
    
    def keys(self):
        """Yield the keys of the items in the pile."""
        return self.order

    def values(self):
        """Yield the values of the items in the pile."""
        yield from (self.pile.get(i) for i in self.order)

    def items(self):
        yield from ((i, self.pile.get(i)) for i in self.order)

    def __getitem__(self, key) -> T | "Pile[T]":
        """
        1. use index, slice, like a list
        2. use ln_id(key), like a dict
        3. use a progression
        4. use a mapping
        5. use another pile
        6. use a set, tuple, iterator...
    
        the idea is as long as the item is LionIDable, it can be used to get items from the pile
        
        if you want a single obj, it return the obj, 
        if there are more than one obj requested, it will return a new pile of obj
        """
        try:
            if isinstance(key, (int, slice)):
                _key = self.order[key]
                _key = [_key] if isinstance(key, int) else _key
                _out = [self.pile.get(i) for i in _key]
                return _out[0] if len(_out) == 1 else pile(_out)
        except IndexError as e:
            raise ItemNotFoundError(key) from e

        keys = _to_list_type(key)
        
        if not all(keys):
            raise LionTypeError("Invalid item type. Expected one or one collection of LionIDable object.")
                
        try:
            if len(keys) == 1:
                return self.pile.get(keys[0])
            return pile([self.pile.get(i) for i in keys])
        except KeyError as e:
            raise ItemNotFoundError(key) from e

    def __setitem__(self, key, item) -> None:
        item = self._validate_pile(item)
        
        if isinstance(key, (int, slice)):
            try:
                _key = self.order[key]
            except IndexError as e:
                raise e
            
            if isinstance(_key, str) and len(item) != 1:
                raise ValueError("Cannot assign multiple items to a single item.")
                
            if isinstance(_key, list) and len(item) != len(_key):
                raise ValueError("The length of values does not match the length of the slice")
                
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
        key = _to_list_type(key)
        items = []

        for i in key:
            i = i if isinstance(i, str) else get_lion_id(i)
            
            if i not in self:
                if default == ...:
                    raise ItemNotFoundError(key)
                return default

            _id = get_lion_id(i)
            items.append(self.pile.pop(_id))
            self.order.remove(_id)        
        
        return pile(items) if len(items) > 1 else items[0]

    def get(self, key: Any, default=...) -> T | "Pile[T]" | None:
        try:
            return self[key]
        except ItemNotFoundError:
            if default == ...:
                raise
            return default

    def update(self, other: any):
        p = pile(self._validate_pile(other))
        self[p] = p
        
    def clear(self):
        self.pile.clear()
        self.order.clear()

    def include(self, item: Any) -> bool:
        """Include items in the pile if not already present."""
        item = _to_list_type(item)
        if item not in self:
            self[item] = item
        return item in self

    def exclude(self, item: Any) -> bool:
        """Exclude items from the pile if not already excluded."""

        if item in self:
            self.pop(item)
        return item not in self

    def is_homogenous(self) -> bool:
        """Check if all items in the pile have the same type."""
        return len(self.pile) < 2 or all(is_same_dtype(self.pile.values()))

    def is_empty(self) -> bool:
        return not self.pile

    @field_validator("item_type", mode="before")
    def _validate_item_type(cls, value):
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
    def _validate_pile(cls, value, /):
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

    def __iter__(self):
        return iter(self.values())

    def __len__(self) -> int:
        """Return the number of items in the pile."""
        return len(self.pile)

    def __add__(self, other: T) -> "Pile":
        """Add an lion item to the pile using the + operator."""
        _copy = self.model_copy(deep=True)
        if _copy.include(other):
            return _copy
        raise LionValueError("Item cannot be included in the pile.")

    def __sub__(self, other):
        _copy = self.model_copy(deep=True)
        if other not in self:
            raise ItemNotFoundError(other)
        _copy.exclude(other)
        return _copy
        
    def __iadd__(self, other: T) -> "Pile":
        """Add an lion item to the pile using the += operator."""
        self.include(other)
        return self

    def __isub__(self, other: LionIDable) -> "Pile":
        return self - other

    def __radd__(self, other: T) -> "Pile":
        """Add an item to the pile using the + operator."""
        return other + self

    def size(self):
        """Return the number of items in the pile."""
        return len(self.pile)

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
    items: Iterable[T] | None = None, item_type: set[Type] | None = None
) -> Pile[T]:
    """Create a new Pile instance."""
    if not items:
        return Pile(item_type=item_type) if item_type else Pile()
    
    a = Pile(pile=items, item_type=item_type)
    a.order = list(a.pile.keys())
    return a