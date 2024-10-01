"""deprecated, use lionabc package"""

from abc import ABC


class Record(ABC):
    """represents a record in a given context."""


class Ordering(ABC):
    """Represents sequencing of certain order."""


class Condition(ABC):
    """Represents a condition in a given context."""


class Actionable(ABC):
    """Represents an action that can be invoked with arguments."""


class Progressable(ABC):
    """Represents a process that can progress forward asynchronously."""


class Relatable(ABC):
    """Defines a relationship that can be established with arguments."""


class Sendable(ABC):
    """Represents an object that can be sent with a sender and recipient."""


class Executable(ABC):
    """Represents an object that can be executed with arguments."""


class Directive(ABC):
    """Represents a directive that can be directed with arguments."""


# for backward compatibility
__all__ = [
    "Record",
    "Ordering",
    "Condition",
    "Actionable",
    "Progressable",
    "Relatable",
    "Sendable",
    "Executable",
    "Directive",
]
