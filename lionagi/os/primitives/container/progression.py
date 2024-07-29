from __future__ import annotations

from typing import Iterator, Any, override, TypeAliasType, TypeGuard

from lion_core.exceptions import ItemNotFoundError
from lion_core.generic.progression import Progression as CoreProgression
from lion_core.generic.util import validate_order


class Progression(CoreProgression):
    """
    A sophisticated, ordered sequence container for managing and manipulating lists of items in the Lion framework.

    The Progression class is a fundamental component designed to maintain an ordered list
    of item identifiers (Lion IDs) while providing a comprehensive set of operations for
    manipulation and access. It seamlessly combines list-like functionality with
    Lion framework-specific features, offering a powerful tool for managing ordered data.

    Key Features:
    1. Ordered Storage: Maintains a strict order of item identifiers (Lion IDs).
    2. Hybrid Access: Supports both integer indexing and Lion ID-based operations.
    3. Rich Manipulation: Offers methods for adding, removing, and reordering items.
    4. Sequence Operations: Implements common sequence operations (len, iter, contain, etc.).
    5. Arithmetic Support: Enables combining progressions through arithmetic operations.
    6. Type Safety: Ensures all stored identifiers are valid Lion IDs.
    7. Named Progressions: Allows optional naming for easy identification.

    Attributes:
        name (str | None): Optional name for the progression. Useful for identification in complex systems.
        order (list[str]): The core ordered list of item identifiers (Lion IDs).

    Usage:
        # Create a new Progression
        prog = Progression(order=['id1', 'id2', 'id3'], name='MyProgression')

        # Add items
        prog.append('id4')
        prog.include(['id5', 'id6'])

        # Access items
        first_id = prog[0]
        slice_prog = prog[1:3]

        # Remove items
        removed_id = prog.pop()
        prog.exclude('id2')

        # Combine progressions
        combined_prog = prog + Progression(['id7', 'id8'])

    The Progression class excels in scenarios requiring:
    - Strict maintenance of item order with flexible manipulation
    - Efficient bidirectional mapping between indices and Lion IDs
    - Complex order-based operations in Lion framework applications

    Methods:
        __init__(order: list[str] | None = None, name: str | None = None)
        __contains__(item: Any) -> bool
        __list__() -> list[str]
        __len__() -> int
        __getitem__(key: int | slice) -> str | Progression
        __setitem__(key: int | slice, value: Any) -> None
        __delitem__(key: int | slice) -> None
        __iter__() -> Iterator[str]
        __next__() -> str
        __eq__(other: object) -> bool
        __bool__() -> bool
        __add__(other: Any) -> Progression
        __radd__(other: Any) -> Progression
        __iadd__(other: Any) -> Progression
        __isub__(other: Any) -> Progression
        __sub__(other: Any) -> Progression
        __repr__() -> str
        __str__() -> str
        size() -> int
        clear() -> None
        append(item: Any) -> None
        pop(index: int | None = None) -> str
        include(item: Any) -> None
        exclude(item: int | Any) -> None
        is_empty() -> bool
        __reverse__() -> Iterator[str]
        index(item: Any, start: int = 0, end: int | None = None) -> int
        remove(item: Any) -> None
        popleft() -> str
        extend(item: Progression | Any) -> None
        count(item: Any) -> int
        insert(index: int, item: Any) -> None

    Note:
        - All methods that accept or return items work with Lion IDs (strings).
        - Operations that modify the progression (e.g., append, exclude) automatically
          validate and convert inputs to ensure only valid Lion IDs are stored.
        - The class provides both mutable (e.g., append) and immutable (e.g., __add__) operations.
          Use immutable operations when you need to preserve the original progression.

    Performance Characteristics:
        - Accessing by index: O(1)
        - Searching by Lion ID: O(n)
        - Appending: Amortized O(1)
        - Insertion/Deletion at arbitrary positions: O(n)
        - Iteration: O(n)

    Thread Safety:
        The Progression class is not inherently thread-safe. When using in a multi-threaded
        environment, external synchronization should be applied to ensure data consistency.

    Error Handling:
        - Invalid indices or Lion IDs raise appropriate exceptions (e.g., ItemNotFoundError).
        - Type mismatches (e.g., trying to extend with a non-Progression) raise LionTypeError.

    Customization:
        The _validate_order method can be overridden in subclasses to implement
        custom validation logic for the order of items.

    See Also:
        Element: Base class providing core Lion framework functionality.
        Ordering: Interface defining ordering operations.
        SysUtil: Utility class for Lion ID operations.
        ItemNotFoundError: Exception raised when an item is not found in the progression.
        LionTypeError: Exception raised for type-related errors.

    Warning:
        Modifying the 'order' attribute directly can lead to inconsistent state.
        Always use the provided methods to manipulate the progression's contents.
    """

    def __init__(self, order: list[str], name: str | None):
        super().__init__(order=order, name=name)

    @override
    def __getitem__(self, key: int | slice) -> str | Progression:
        """
        Get an item or slice of items from the progression.

        Args:
            key: An integer index or slice object.

        Returns:
            str | Progression: The item at the given index or a new Progression with the sliced items.

        Raises:
            ItemNotFoundError: If the requested index or slice is out of range.
        """
        if not isinstance(key, int | slice):
            raise TypeError(
                f"indices must be integers or slices, not {key.__class__.__name__}"
            )

        try:
            a = self.order[key]
            if not a:
                raise ItemNotFoundError(f"index {key} item not found")
            if isinstance(key, slice):
                return Progression(order=a)
            else:
                return a
        except IndexError:
            raise ItemNotFoundError(f"index {key} item not found")

    @override
    def __sub__(self, other: Any) -> Progression:
        """
        Remove an item or items from the progression.

        Args:
            other: The item(s) to remove.

        Returns:
            Progression: A new Progression without the specified item(s).
        """
        other = validate_order(other)
        new_order = list(self)
        for i in other:
            new_order.remove(i)
        return Progression(order=new_order)

    @override
    def __add__(self, other: Any) -> Progression:
        """
        Add an item or items to the end of the progression.

        Args:
            other: The item(s) to add.

        Returns:
            Progression: A new Progression with the added item(s).
        """
        other = validate_order(other)
        new_order = list(self)
        new_order.extend(other)
        return Progression(order=new_order)

    @override
    def __reverse__(self) -> "Progression":
        """
        Return a reversed progression.

        Returns:
            Iterator[str]: An iterator over the reversed Lion IDs in the progression.
        """
        return Progression(reversed(self.order), name=self.name)


def prog_call(cls: Any, order: Any, name: str | None = None) -> TypeGuard[Progression]:
    if isinstance(order, Progression):
        return order
    if isinstance(order, CoreProgression):
        return Progression(list(order), name)
    try:
        return Progression(order, name)
    except ValueError as e:
        raise ValueError(f"Invalid Progression input: {e}")

prog = TypeAliasType("prog", Progression)
prog.__call__ = prog_call


__all__ = ["Progression", "prog"]

# File: lionagi/os/generic/progression.py