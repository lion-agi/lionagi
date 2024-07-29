from typing import Any, Type, TypeVar, TypeAliasType, TypeGuard
from lion_core.setting import LN_UNDEFINED
from lion_core.abc import Observable
from lion_core.exceptions import ItemNotFoundError
from lion_core.generic import (
    to_list_type,
    validate_order,
    Pile as CorePile,
    Progression as CoreProgression,
)

from lionagi.os.sys_util import SysUtil


T = TypeVar("T", bound=Observable)


class Pile(CorePile):
    """
    A sophisticated, ordered collection of Elements with hybrid list and dictionary-like access.

    The Pile class serves as a core container in the Lion framework, designed to efficiently
    store and manage collections of Element objects. It maintains both the order of items
    and allows fast access by unique identifiers, providing a versatile data structure
    for various use cases within the framework.

    Key Features:
    1. Hybrid Access: Supports both list-like (index/slice) and dict-like (key) access.
    2. Type Safety: Optionally enforces item type restrictions.
    3. Order Preservation: Maintains a specific order of items using a Progression.
    4. Flexible Inclusion/Exclusion: Provides methods for adding and removing items.
    5. Iteration Support: Allows iteration over items in their specified order.
    6. Set-like Operations: Supports operations like union and difference.
    7. Generic Typing: Uses Generic[T] for type hinting of contained items.

    Attributes:
        pile_ (dict[str, T]): Internal storage mapping identifiers to items.
        item_type (set[Type[Observable]] | None): Set of allowed item types.
        order (Progression): Progression maintaining the order of item identifiers.
        strict (bool): Flag to enforce strict type checking when item_type is defined.

    Type Parameters:
        T: The type of items stored in the Pile, must be a subclass of Observable.

    Usage:
        # Create a Pile with specific item type
        my_pile = Pile(item_type={CustomElement})
        
        # Add items
        my_pile.include(CustomElement())
        
        # Access items
        item = my_pile[0]  # By index
        item = my_pile['item_id']  # By ID
        
        # Iterate over items
        for item in my_pile:
            print(item)

    The Pile class is particularly useful in scenarios requiring:
    - Ordered storage of items with fast random access
    - Type-safe collections with flexible access patterns
    - Complex data structures needing both list and dict-like operations

    Methods:
        __init__(items: Any = None, item_type: set[Type[Observable]] | None = None,
                 order: Progression | list | None = None, strict: bool = False)
        __getitem__(key: Any) -> T | "Pile"
        __setitem__(key: Any, item: Any) -> None
        __contains__(item: Any) -> bool
        __len__() -> int
        __iter__() -> Iterable
        __str__() -> str
        __repr__() -> str
        __bool__() -> bool
        __list__() -> list
        __add__(other: T) -> Pile
        __sub__(other: Any) -> Pile
        __iadd__(other: T) -> Pile
        __isub__(other: Any) -> Pile
        __radd__(other: T) -> Pile
        keys() -> list
        values() -> list
        items() -> list[tuple[str, T]]
        get(key: Any, default=LN_UNDEFINED) -> T | "Pile" | None
        pop(key: Any, default=LN_UNDEFINED) -> T | "Pile" | None
        remove(item: T) -> None
        include(item: Any) -> None
        exclude(item: Any) -> None
        clear() -> None
        update(other: Any) -> None
        is_empty() -> bool
        size() -> int
        append(item: T) -> None
        insert(index: int, item: Any) -> None

    Notes:
        - The Pile class inherits from Element, providing a unique identifier,
          and Collective, defining it as a collection type.
        - It uses a combination of a dictionary (pile_) for fast access and a
          Progression (order) to maintain item order.
        - The class supports generic typing, allowing for type-safe collections
          of specific Observable subclasses.
        - When strict mode is enabled, only items of the exact specified type(s)
          are allowed; otherwise, subclasses are also accepted.

    Performance Considerations:
        - Access by ID (dict-like) is O(1), while access by index (list-like) is O(1) on average.
        - Inclusion and exclusion operations are generally O(1), but may be O(n) in worst-case
          scenarios involving order manipulation.
        - Iteration over items is efficient, yielding items in the specified order.

    Thread Safety:
        While basic read operations are thread-safe, concurrent modifications
        should be properly synchronized to ensure data consistency.

    See Also:
        Element: Base class providing core Lion framework functionality.
        Collective: Interface defining collection operations.
        Observable: Base class for items that can be stored in a Pile.
        Progression: Class used for maintaining item order.
    """
    
    def __init__(
        self,
        items: Any = None,
        item_type: set[Type[Observable]] | None = None,
        order: CoreProgression | list | None = None,
        strict: bool = False,
    ):
        super().__init__(
            items=items, 
            item_type=item_type,
            order=order,
            strict=strict
        )

    def __getitem__(self, key) -> T | "Pile":
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
        if key is None:
            raise ValueError("getitem key not provided.")
        if isinstance(key, int):
            try:
                result_id = self.order[key]
                return self.pile_[result_id]
            except Exception as e:
                raise ItemNotFoundError(f"index {key}. Error: {e}")

        elif isinstance(key, slice):
            try:
                result_ids = self.order[key]
                result = []
                for i in result_ids:
                    result.append(self.pile_[i])
                return Pile(items=result, item_type=self.item_type)
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
                else:
                    return Pile(items=result, item_type=self.item_type)
            except Exception as e:
                raise ItemNotFoundError(f"Key {key}. Error:{e}")

    def get(self, key: Any, default=LN_UNDEFINED) -> T | "Pile" | None:
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
                else:
                    return Pile(items=result, item_type=self.item_type)
            except Exception as e:
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default

    def pop(self, key: Any, default=LN_UNDEFINED) -> T | "Pile" | None:
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
                pop_items = self.order[key]
                pop_items = [pop_items] if isinstance(pop_items, str) else pop_items
                result = []
                for i in pop_items:
                    self.order.remove(i)
                    result.append(self.pile_.pop(i))
                result = (
                    Pile(items=result, item_type=self.item_type)
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
                else:
                    return Pile(items=result, item_type=self.item_type, order=key)
            except Exception as e:
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default

    def __add__(self, other: T) -> "Pile":
        """
        Create a new pile by including item(s) using `+`.

        Args:
            other: Item(s) to include. Can be single item or collection.

        Returns:
            Pile: New Pile with all items from current pile plus item(s).

        Raises:
            LionItemError: If item(s) can't be included.
        """
        result = Pile(items=self.values(), item_type=self.item_type, order=self.order)
        result.include(other)
        return result

    def __sub__(self, other) -> "Pile":
        """
        Create a new pile by excluding item(s) using `-`.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            Pile: New Pile with all items from current pile except item(s).

        Raises:
            ItemNotFoundError: If item(s) not found in pile.
        """
        result = Pile(items=self.values(), item_type=self.item_type, order=self.order)
        result.pop(other)
        return result

    def __isub__(self, other) -> "Pile":
        """
        Exclude item(s) from the current pile in place using `-=`.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            Pile: The modified pile.
        """
        result = Pile(items=self.values(), item_type=self.item_type, order=self.order)
        result.pop(other)
        self.remove(other)
        return self



def pile_call(
    cls, 
    items: Any = None,
    item_type: set[Type[Observable]] | None = None,
    order: CoreProgression | list | None = None,
    strict: bool = False,
) -> TypeGuard[Pile]:
    if isinstance(items, Pile):
        return items
    if isinstance(items, CorePile):
        return Pile(list(items), item_type or items.item_type, order, strict)
    try:
        return Pile(items, item_type, order, strict)
    except Exception as e:
        raise ValueError(f"Invalid pile value. Error: {e}")    


pile = TypeAliasType("pile", Pile)
pile.__call__ = pile_call


__all__ = ["Pile", "pile"]
