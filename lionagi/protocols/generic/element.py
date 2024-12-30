# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime
from typing import Any, Self, TypeVar
from uuid import UUID, uuid4

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from lionagi._class_registry import LION_CLASS_REGISTRY, get_class
from lionagi._errors import IDError
from lionagi.settings import Settings
from lionagi.utils import UNDEFINED, time

from .concepts import Observable

__all__ = (
    "Element",
    "IDType",
    "E",
    "Observable",
)


class IDType:
    """A class representing a unique identifier (UUID4-based).

    This class provides creation, validation, and comparison functionality
    for UUID4-based identifiers.
    """

    __slots__ = ("_id",)

    def __init__(self, id: UUID4) -> None:
        """Initialize the IDType instance.

        Args:
            id (UUID4): A valid UUID4 object.
        """
        self._id = id

    @classmethod
    def validate(cls, value: UUID4 | str) -> IDType:
        """Validate and convert a value into an IDType instance.

        If the value is already an IDType, it is returned directly.
        Otherwise, an attempt is made to parse the value as a UUID4.

        Args:
            value (UUID4 | str): The value to validate. It can be a UUID4,
                a string representation of a UUID4, or an IDType itself.

        Returns:
            IDType: A valid IDType instance.

        Raises:
            IDError: If the value is not a valid UUID4.
        """
        if isinstance(value, IDType):
            return value
        try:
            return cls(id=UUID(str(value), version=4))
        except ValueError:
            raise IDError("Invalid ID format.")

    @classmethod
    def create(cls) -> IDType:
        """Create a new IDType with a randomly generated UUID4.

        Returns:
            IDType: A new IDType instance with a random UUID4.
        """
        return cls(uuid4())

    def __str__(self) -> str:
        """Return the string representation of the ID.

        Returns:
            str: The string form of the UUID4.
        """
        return str(self._id)

    def __repr__(self) -> str:
        """Return the official string representation of the IDType instance.

        Returns:
            str: The official string representation.
        """
        return f"IDType({self._id})"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another IDType.

        Args:
            other (Any): Another object to compare.

        Returns:
            bool: True if the other object is an IDType with the same UUID4,
                False otherwise.
        """
        if not isinstance(other, IDType):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        """Compute a hash value for this IDType.

        Returns:
            int: The hash value based on the UUID4.
        """
        return hash(self._id)


class Element(BaseModel, Observable):
    """Base class for uniquely identifiable, timestamped elements.

    This class extends pydantic's BaseModel to provide attributes for
    unique identification (UUID4-based) and creation timestamps.
    """

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    id: IDType = Field(default_factory=IDType.create)
    created_at: float = Field(
        default_factory=lambda: time(type_="timestamp"),
        description="Creation timestamp",
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Register subclass in LION_CLASS_REGISTRY upon creation."""
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.__name__] = cls

    @field_serializer("id")
    def _serialize_id(self, id: IDType) -> str:
        """Serialize the IDType into its string representation.

        Args:
            id (IDType): The IDType object to serialize.

        Returns:
            str: The string representation of the ID.
        """
        return str(id)

    @field_validator("id", mode="before")
    def _validate_id(cls, value: Any) -> IDType:
        """Validate the `id` field to be a valid IDType.

        Args:
            value (Any): The raw value to validate.

        Returns:
            IDType: A valid IDType instance.

        Raises:
            IDError: If the value is not a valid UUID4 string or object.
        """
        return IDType.validate(value)

    @field_validator("created_at", mode="before")
    def _validate_created_at(cls, value: Any) -> float:
        """Validate and convert the `created_at` field into a float timestamp.

        Args:
            value (Any): The raw value to validate, which can be a datetime,
                int, float, or ISO8601-formatted string.

        Returns:
            float: The POSIX timestamp representation.

        Raises:
            ValueError: If the value cannot be converted into a valid timestamp.
        """
        if isinstance(value, datetime):
            return value.timestamp()

        if isinstance(value, (int, float)):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).timestamp()
            except Exception as e:
                try:
                    value = float(value)
                except Exception:
                    raise ValueError(
                        f"Invalid datetime string format: {value}"
                    ) from e

        try:
            return datetime.fromtimestamp(value, tz=Settings.Config.TIMEZONE)
        except Exception as e:
            raise ValueError(f"Invalid datetime string format: {value}") from e

    @property
    def created_datetime(self) -> datetime:
        """Convert the `created_at` timestamp into a datetime object.

        Returns:
            datetime: The datetime object corresponding to `created_at`.
        """
        return datetime.fromtimestamp(
            self.created_at, tz=Settings.Config.TIMEZONE
        )

    @classmethod
    def class_name(cls) -> str:
        """Return the class name of the element.

        Returns:
            str: The class name.
        """
        return cls.__name__

    def __eq__(self, other: Any) -> bool:
        """Check equality with another Element based on the ID.

        Args:
            other (Any): Another object to compare.

        Returns:
            bool: True if `other` is an Element with the same ID, False otherwise.
        """
        if not isinstance(other, Element):
            return NotImplemented
        return self.id == other.id

    def __str__(self) -> str:
        """Return a user-friendly string representation of the Element.

        Returns:
            str: A string consisting of the class name and the ID.
        """
        return f"{self.class_name()}({self.id})"

    __repr__ = __str__

    def __bool__(self) -> bool:
        """Return the truth value of the Element instance.

        Returns:
            bool: Always True, as an Element is considered truthy if it exists.
        """
        return True

    def __len__(self) -> int:
        """Return the length of the Element.

        Returns:
            int: Always 1, representing a single object.
        """
        return 1

    def __hash__(self) -> int:
        """Compute a hash value for the Element based on its ID.

        Returns:
            int: The hash value derived from the ID.
        """
        return hash(self.id)

    def to_dict(self) -> dict:
        """Convert the Element instance into a dictionary representation.

        Returns:
            dict: A dictionary containing Element data. The special key
            'lion_class' is added for round-trip deserialization.
        """
        dict_ = self.model_dump()
        dict_["lion_class"] = self.class_name()
        # Filter out UNDEFINED fields
        for k in list(dict_.keys()):
            if dict_[k] is UNDEFINED:
                dict_.pop(k)
        return dict_

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:
        """Deserialize an Element (or subclass) from a dictionary.

        Args:
            dict_ (dict): A dictionary containing Element data. If it includes
                'lion_class', and that class differs from the current one, it
                will delegate deserialization to that subclass if it overrides
                this method.

        Returns:
            Self: An instance of the appropriate Element or subclass.
        """
        lion_class = dict_.pop("lion_class", None)
        if lion_class and lion_class != cls.__name__:
            subcls = get_class(lion_class)
            # Only delegate if the subclass defines a custom from_dict
            if subcls.from_dict.__func__ != Element.from_dict.__func__:
                return subcls.from_dict(dict_)
        return cls.model_validate(dict_)


E = TypeVar("E", bound=Element)

# File: lionagi/protocols/generic/element.py
