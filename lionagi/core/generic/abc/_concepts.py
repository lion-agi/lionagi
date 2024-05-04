"""This module defines abstract base classes for the LionAGI"""

from collections.abc import Generator
from abc import ABC, abstractmethod
from typing import Any, Iterator, Tuple, TypeVar
from ._component import LionIDable

T = TypeVar("T")


class Relatable(ABC): ...


class Record(ABC):
    """
    Abstract base class for a collection of unique LionAGI items.
    This class defines the required methods for managing the items in the record.
    Methods accept `LionIDable` for retrieval and require Component instances for addition.
    """

    @abstractmethod
    def keys(self) -> Generator[str, None, None]:
        """Return an iterator over the ln_id of items in the record."""

    @abstractmethod
    def values(self) -> Generator[T, None, None]:
        """Return an iterator over items in the record."""

    @abstractmethod
    def items(self) -> Generator[Tuple[str, T], None, None]:
        """Return an iterator of (ln_id, item) tuples in the record."""

    @abstractmethod
    def get(self, item: LionIDable, /, default: Any = None) -> T:
        """
        Retrieve an item in collection by identifier. Accepts a LionIDable object (ID or Component).
        """

    # @abstractmethod
    # def pop(self, item: LionIDable, default=..., /) -> T | None:
    #     """
    #     Remove and return an item by identifier. Accepts a LionIDable object (ID or Component).
    #     """

    # @abstractmethod
    # def remove(self, item: LionIDable, /) -> None:
    #     """
    #     Remove item from the record. Accepts a LionIDable object (ID or Component).
    #     Will raise a KeyError if the item is not found.
    #     """

    # @abstractmethod
    # def clear(self) -> None:
    #     """remove all items from the record"""

    # @abstractmethod
    # def update(self, other: Any) -> None:
    #     """add items from other record to this record"""

    # @abstractmethod
    # def include(self, item: T, /) -> bool:
    #     """
    #     Add item to the record, will ignore if item already exists.
    #     Return boolean indicating if the item is in the pile.
    #     """

    # @abstractmethod
    # def exclude(self, item: LionIDable, /) -> bool:
    #     """
    #     Remove item from the record. Accepts a LionIDable object (ID or Component).
    #     Return boolean indicating if the item was removed.
    #     """

    # @abstractmethod
    # def is_empty(self) -> bool:
    #     """return boolean indicating if the record contains no item"""

    def __bool__(self):
        return True

    @abstractmethod
    def __getitem__(self, item: LionIDable) -> T:
        """
        Return an item from the record using a LionIDable identifier.
        Will raise KeyError if item id is not found.
        """

    @abstractmethod
    def __setitem__(self, item: LionIDable, value: T) -> None:
        """
        Add or update an item in the record. Requires a Component instance to be provided as value.
        """

    @abstractmethod
    def __contains__(self, item: LionIDable) -> bool:
        """Check if an item is in the record, using either an ID or object."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of items in the record."""

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """Iterate over items in the record."""


class Ordering(ABC):
    """represents sequencing of certain order"""

    # @abstractmethod
    # def __iadd__(self, other: Any) -> "Ordering":
    #     """
    #     Add a item id or a sequence of item ids to the ordering (right side).
    #     Return self.
    #     """

    # @abstractmethod
    # def __radd__(self, other: Any) -> "Ordering":
    #     """
    #     Add a item id or a sequence of item ids to the ordering (right side of self).
    #     Return self.
    #     """

    # @abstractmethod
    # def __add__(self, other: Any) -> "Ordering":
    #     """Add a item id or a sequence of item ids to the ordering."""

    # @abstractmethod
    # def __isub__(self, other: Any) -> "Ordering":
    #     """
    #     Remove a item id or a sequence of item ids from the ordering (left side).
    #     Return self.
    #     """

    @abstractmethod
    def __len__(self):
        """number of items ids in the ordering, or number of orderings in another ordering"""

    # @abstractmethod
    # def __iter__(self):
    #     """iterate over items ids in the ordering"""

    # @abstractmethod
    # def __next__(self) -> Any:
    #     """Return the next item id in the ordering."""

    @abstractmethod
    def __contains__(self, item: Any) -> bool:
        """Check if an item id is in the ordering."""


class Condition(ABC):
    """Represents a situation."""

    @abstractmethod
    async def applies(self, value: Any, /, *args: Any, **kwargs: Any) -> Any:
        """Check if the condition applies to the given value."""


class Actionable(ABC):
    """Represents a purposed process."""

    @abstractmethod
    async def invoke(self, /, *args: Any, **kwargs: Any) -> Any:
        """Invoke the action with the given arguments."""


class Workable(ABC):
    """Represents a processable entity."""

    @abstractmethod
    async def perform(self, /, *args: Any, **kwargs: Any) -> Any:
        """Perform the work with the given arguments."""


class Rule(Condition, Actionable):

    def __init__(self, **kwargs):
        self.validation_kwargs = kwargs
        self.fix = kwargs.get("fix", False)

    @abstractmethod
    async def applies(self, /, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    async def invoke(self, /, *args: Any, **kwargs: Any) -> Any: ...
