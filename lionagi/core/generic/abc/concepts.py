"""This module defines abstract base classes for LionAGI."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Iterator, TypeVar

from pydantic import Field, BaseModel, field_validator
from .component import LionIDable, get_lion_id
from .exceptions import LionTypeError


T = TypeVar("T")


class Record(ABC):
    """Abstract base class for managing a collection of unique LionAGI items.

    Accepts LionIDable for retrieval and requires Component instances for
    addition.
    """

    @abstractmethod
    def keys(self) -> Generator[str, None, None]:
        """Return an iterator over the ln_id of items in the record."""

    @abstractmethod
    def values(self) -> Generator[T, None, None]:
        """Return an iterator over items in the record."""

    @abstractmethod
    def get(self, item: LionIDable, /, default: Any = None) -> T:
        """
        Retrieve an item by identifier.

        Accepts a LionIDable object. Returns the default if the item is not
        found.
        """

    def __bool__(self) -> bool:
        return True

    @abstractmethod
    def __getitem__(self, item: LionIDable) -> T:
        """
        Return an item using a LionIDable identifier.

        Raises KeyError if the item ID is not found.
        """

    @abstractmethod
    def __setitem__(self, item: LionIDable, value: T) -> None:
        """Add or update an item in the record.

        The value must be a Component instance.
        """

    @abstractmethod
    def __contains__(self, item: LionIDable) -> bool:
        """Check if an item is in the record, using either an ID or an object."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of items in the record."""

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """Iterate over items in the record."""


class Ordering(ABC):
    """Represents sequencing of certain order."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of item ids in the ordering.

        Or the number of orderings in another ordering.
        """

    @abstractmethod
    def __contains__(self, item: Any) -> bool:
        """Check if an item id is in the ordering."""


class Condition(ABC):
    """Represents a condition in a given context."""

    @abstractmethod
    async def applies(self, value: Any, /, *args: Any, **kwargs: Any) -> Any:
        """Asynchronously determine if the condition applies to the given value."""


class Actionable(ABC):
    """Represents an action that can be invoked with arguments."""

    @abstractmethod
    async def invoke(self, /, *args: Any, **kwargs: Any) -> Any:
        """Invoke the action asynchronously with the given arguments."""


class Progressable(ABC):
    """Represents a process that can progress forward asynchronously."""

    @abstractmethod
    async def forward(self, /, *args: Any, **kwargs: Any) -> None:
        """Move the process forward asynchronously."""


class Relatable(ABC):
    """Defines a relationship that can be established with arguments."""

    @abstractmethod
    def relate(self, /, *args: Any, **kwargs: Any) -> None:
        """Establish a relationship based on the provided arguments."""


class Sendable(BaseModel, ABC):

    sender: str = Field(
        "N/A",
        title="Sender",
        description=("The id of the sender node, or 'system', 'user', or 'assistant'."),
    )

    recipient: str = Field(
        "N/A",
        title="Recipient",
        description=(
            "The id of the recipient node, or 'system', 'user', or 'assistant'."
        ),
    )

    @field_validator("sender", "recipient", mode="before")
    def _validate_sender_recipient(cls, value):
        """Validate the sender and recipient fields."""
        if value is None:
            return "N/A"

        if value in ["system", "user", "N/A"]:
            return value

        a = get_lion_id(value)
        if not isinstance(a, str) or len(a) != 32:
            raise LionTypeError(
                "Invalid sender or recipient value. "
                "Expected a valid node id or one of "
                "'system' or 'user'."
            )
        return a


class Executable(ABC):

    @abstractmethod
    async def execute(self, /, *args: Any, **kwargs: Any) -> Any:
        """Execute the object with the given arguments asynchronously."""
        pass
