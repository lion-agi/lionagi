"""This module defines abstract base classes for LionAGI."""
import warnings
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Iterator, TypeVar

from pydantic import Field, BaseModel, field_validator

from .component import LionIDable, get_lion_id
from .exceptions import LionTypeError

T = TypeVar("T")

from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


# @deprecated(
#     format_deprecated_msg(
#         deprecated_name="lionagi.core.collections.abc.concepts.Record",
#         deprecated_version="v0.3.0",
#         removal_version="v1.0",
#         replacement="check `lion_core.abc._record` for updates",
#     ),
#     category=DeprecationWarning,
# )
class Record(ABC):
    """
    Abstract base class for managing a collection of unique LionAGI items.

    Accepts LionIDable for retrieval and requires Component instances for
    addition.

    Methods:
        keys: Return an iterator over the ln_id of items in the record.
        values: Return an iterator over items in the record.
        get: Retrieve an item by identifier.
        __getitem__: Return an item using a LionIDable identifier.
        __setitem__: Add or update an item in the record.
        __contains__: Check if an item is in the record.
        __len__: Return the number of items in the record.
        __iter__: Iterate over items in the record.
    """

    def __init__(self):
        warnings.warn(
            format_deprecated_msg(
                deprecated_name="lionagi.core.collections.abc.concepts.Record",
                deprecated_version="v0.3.0",
                removal_version="v1.0",
                replacement="check `lion_core.abc._record` for updates",
            ),
            category=DeprecationWarning,
        )

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

        Args:
            item (LionIDable): The identifier of the item to retrieve.
            default (Any): The default value to return if the item is not found.

        Returns:
            T: The retrieved item or the default value.
        """

    @abstractmethod
    def __getitem__(self, item: LionIDable) -> T:
        """
        Return an item using a LionIDable identifier.

        Raises:
            KeyError: If the item ID is not found.

        Args:
            item (LionIDable): The identifier of the item to retrieve.

        Returns:
            T: The retrieved item.
        """

    @abstractmethod
    def __setitem__(self, item: LionIDable, value: T) -> None:
        """
        Add or update an item in the record.

        The value must be a Component instance.

        Args:
            item (LionIDable): The identifier of the item to add or update.
            value (T): The Component instance to add or update.
        """

    @abstractmethod
    def __contains__(self, item: LionIDable) -> bool:
        """
        Check if an item is in the record, using either an ID or an object.

        Args:
            item (LionIDable): The identifier or object to check.

        Returns:
            bool: True if the item is in the record, False otherwise.
        """

    @abstractmethod
    def __len__(self) -> int:
        """
        Return the number of items in the record.

        Returns:
            int: The number of items in the record.
        """

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """
        Iterate over items in the record.

        Yields:
            T: The items in the record.
        """


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.concepts.Ordering",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion_core.abc._space` for updates",
    ),
    category=DeprecationWarning,
)
class Ordering(ABC):
    """Represents sequencing of certain order."""

    @abstractmethod
    def __len__(self) -> int:
        """
        Return the number of item ids in the ordering.

        Or the number of orderings in another ordering.
        """

    @abstractmethod
    def __contains__(self, item: Any) -> bool:
        """Check if an item id is in the ordering."""


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.concepts.Condition",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion_core.abc._observation` for updates",
    ),
    category=DeprecationWarning,
)
class Condition(ABC):
    """Represents a condition in a given context."""

    @abstractmethod
    async def applies(self, value: Any, /, *args: Any, **kwargs: Any) -> Any:
        """Asynchronously determine if the condition applies to the given value.

        Args:
            value (Any): The value to check against the condition.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result of applying the condition to the value.
        """


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.concepts.Actionable",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement=None,
    ),
    category=DeprecationWarning,
)
class Actionable(ABC):
    """Represents an action that can be invoked with arguments."""

    @abstractmethod
    async def invoke(self, /, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the action asynchronously with the given arguments.

        Args:
            *args: Positional arguments for invoking the action.
            **kwargs: Keyword arguments for invoking the action.

        Returns:
            Any: The result of invoking the action.
        """


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.concepts.Progressable",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement=None,
    ),
    category=DeprecationWarning,
)
class Progressable(ABC):
    """Represents a process that can progress forward asynchronously."""

    @abstractmethod
    async def forward(self, /, *args: Any, **kwargs: Any) -> None:
        """Move the process forward asynchronously.

        Args:
            *args: Positional arguments for moving the process forward.
            **kwargs: Keyword arguments for moving the process forward.
        """


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.concepts.Relatable",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion_core.abc._chracteristic.Relational` for updates",
    ),
    category=DeprecationWarning,
)
class Relatable(ABC):
    """Defines a relationship that can be established with arguments."""

    @abstractmethod
    def relate(self, /, *args: Any, **kwargs: Any) -> None:
        """Establish a relationship based on the provided arguments.

        Args:
            *args: Positional arguments for establishing the relationship.
            **kwargs: Keyword arguments for establishing the relationship.
        """


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.concepts.Sendable",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core.abc._characteristic.Communicatable` for updates",
    ),
    category=DeprecationWarning,
)
class Sendable(BaseModel, ABC):
    """Represents an object that can be sent with a sender and recipient."""

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
        """Validate the sender and recipient fields.

        Args:
            value (Any): The value to validate.

        Returns:
            str: The validated value.

        Raises:
            LionTypeError: If the value is invalid.
        """
        if value is None:
            return "N/A"

        if value in ["system", "user", "N/A", "assistant"]:
            return value

        a = get_lion_id(value)
        if not isinstance(a, str) or len(a) != 32:
            raise LionTypeError(
                "Invalid sender or recipient value. "
                "Expected a valid node id or one of "
                "'system' or 'user'."
            )
        return a


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.concepts.Executable",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion_core.abc._observer.BaseExecutor` package for updates",
    ),
    category=DeprecationWarning,
)
class Executable(ABC):
    """Represents an object that can be executed with arguments."""

    @abstractmethod
    async def execute(self, /, *args: Any, **kwargs: Any) -> Any:
        """Execute the object with the given arguments asynchronously.

        Args:
            *args: Positional arguments for executing the object.
            **kwargs: Keyword arguments for executing the object.

        Returns:
            Any: The result of executing the object.
        """


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.collections.abc.concepts.Directive",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement=None,
    ),
    category=DeprecationWarning,
)
class Directive(ABC):
    """Represents a directive that can be directed with arguments."""

    # @abstractmethod
    # async def direct(self, *args, **kwargs):
    #     """Direct the directive with the given arguments asynchronously.

    #     Args:
    #         *args: Positional arguments for directing the directive.
    #         **kwargs: Keyword arguments for directing the directive.
    #     """

    @property
    def class_name(self) -> str:
        """Get the class name of the directive.

        Returns:
            str: The class name of the directive.
        """
        return self._class_name()

    @classmethod
    def _class_name(cls) -> str:
        """Get the class name of the directive.

        Returns:
            str: The class name of the directive.
        """
        return cls.__name__
