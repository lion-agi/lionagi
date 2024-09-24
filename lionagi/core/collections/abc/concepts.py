from lion_core.abc import BaseRecord, Ordering, Condition   # backward compatible
from abc import ABC, abstractmethod
from typing import Any, TypeVar


T = TypeVar("T")


class Progressable(ABC):
    """Represents a process that can progress forward asynchronously."""

    @abstractmethod
    async def forward(self, /, *args: Any, **kwargs: Any) -> None:
        """Move the process forward asynchronously.

        Args:
            *args: Positional arguments for moving the process forward.
            **kwargs: Keyword arguments for moving the process forward.
        """


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


class Directive(ABC):
    """Represents a directive that can be directed with arguments."""


__all__ = [
    "Ordering",
    "Condition",
    "BaseRecord",
    "Progressable",
    "Executable",
    "Directive",
]