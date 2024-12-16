# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime

from lionagi.core._class_registry import LION_CLASS_REGISTRY, get_class
from lionagi.core.typing import (
    ID,
    Any,
    BaseModel,
    ConfigDict,
    Field,
    IDError,
    LnID,
    Note,
    Observable,
    TypeVar,
    field_validator,
    override,
)
from lionagi.libs.utils import time
from lionagi.settings import Settings

T = TypeVar("T", bound=Observable)


class Element(BaseModel, Observable):
    """Base class in the Lion framework.

    The Element class provides core functionality that all Lion framework components
    inherit. It implements:

    - Unique identification via Lion IDs
    - Creation timestamps with timezone awareness
    - Serialization to/from dictionaries
    - Class registry for subclass management
    - Type validation and conversion
    - String representation formatting

    Key Features:
        - Automatic unique ID generation
        - Immutable timestamps
        - Timezone-aware datetime handling
        - Dictionary serialization
        - Subclass registration
        - Type validation
        - String formatting

    Attributes:
        ln_id (LnID): Unique identifier for the element. Generated automatically
            and immutable.
        timestamp (float): Creation timestamp as Unix timestamp. Generated
            automatically and immutable.
    """

    ln_id: LnID = Field(
        default_factory=ID.id,
        title="Lion ID",
        description="Unique identifier for the element",
        frozen=True,
    )

    timestamp: float = Field(
        default_factory=lambda: time(type_="timestamp"),
        title="Creation Timestamp",
        frozen=True,
        alias="created",
    )

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    @classmethod
    def class_name(cls) -> str:
        """Get the name of the class.

        Returns:
            str: The name of the class.
        """
        return cls.__name__

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.__name__] = cls

    @property
    def created_datetime(self) -> datetime:
        """Get the creation datetime of the Element.

        Converts the Unix timestamp to a timezone-aware datetime object using the
        timezone specified in Settings.Config.TIMEZONE.

        Returns:
            datetime: A timezone-aware datetime object representing when the
                Element was created.
        """
        return datetime.fromtimestamp(
            self.timestamp, tz=Settings.Config.TIMEZONE
        )

    @field_validator("ln_id", mode="before")
    def _validate_id(cls, value: ID.ID) -> str:
        try:
            return ID.get_id(value)
        except Exception:
            raise IDError(f"Invalid lion id: {value}")

    @field_validator("timestamp", mode="before")
    def _validate_timestamp(cls, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, datetime):
            return value.timestamp()
        try:
            if isinstance(value, str):
                try:
                    return float(value)
                except Exception:
                    return datetime.fromisoformat(value).timestamp()
            raise ValueError
        except Exception as e:
            raise ValueError(f"Invalid datetime string format: {value}") from e

    @override
    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> T:
        """Create an instance of the Element or its subclass from a dictionary.

        This method handles dynamic class loading based on the 'lion_class' field
        in the data dictionary. If the target class has its own from_dict
        implementation, that is used instead.

        Args:
            data: Dictionary containing the element data.
            **kwargs: Additional arguments for model validation.

        Returns:
            T: An instance of the Element class or appropriate subclass.
        """
        if "lion_class" in data:
            cls = get_class(class_name=data.pop("lion_class"))
        if cls.from_dict.__func__ != Element.from_dict.__func__:
            return cls.from_dict(data, **kwargs)
        return cls.model_validate(data, **kwargs)

    @override
    def to_dict(self, **kwargs: Any) -> dict:
        """Convert the Element to a dictionary representation.

        The dictionary includes all model fields and adds a 'lion_class' field
        to enable proper reconstruction of the correct class.

        Args:
            **kwargs: Additional arguments to pass to model_dump.

        Returns:
            dict: A dictionary representation of the Element.
        """
        dict_ = self.model_dump(**kwargs)
        dict_["lion_class"] = self.class_name()
        return dict_

    @override
    def __str__(self) -> str:
        timestamp_str = self.created_datetime.isoformat(timespec="minutes")
        return (
            f"{self.class_name()}(ln_id={self.ln_id[:6]}.., "
            f"timestamp={timestamp_str})"
        )

    def __hash__(self) -> int:
        return hash(self.ln_id)

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return 1

    def to_note(self) -> Note:
        """Convert Log to Note.

        Returns:
            Note representation of the log
        """
        return Note(**self.to_dict())


__all__ = ["Element"]
