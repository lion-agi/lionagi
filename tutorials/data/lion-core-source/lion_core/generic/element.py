from datetime import datetime
from typing import Any, TypeVar

from lionabc.exceptions import LionIDError
from pydantic import ConfigDict, field_validator
from typing_extensions import override

from lion_core._class_registry import LION_CLASS_REGISTRY, get_class
from lion_core.generic.base import RealElement
from lion_core.setting import DEFAULT_TIMEZONE
from lion_core.sys_utils import SysUtil

T = TypeVar("T", bound="Element")


class Element(RealElement):
    """Base class in the Lion framework."""

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize and register subclasses in the global class registry."""
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.__name__] = cls

    @property
    def created_datetime(self) -> datetime:
        """Get the creation datetime of the Element."""
        return datetime.fromtimestamp(self.timestamp, tz=DEFAULT_TIMEZONE)

    @field_validator("ln_id", mode="before")
    def _validate_id(cls, value: Any) -> str:
        try:
            return SysUtil.get_id(value)
        except Exception:
            raise LionIDError(f"Invalid lion id: {value}")

    @field_validator("timestamp", mode="before")
    def _validate_timestamp(cls, value: Any) -> float:
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Invalid datetime string format: {value}")
        if isinstance(value, datetime):
            return value.timestamp()
        elif isinstance(value, float | int):
            return value
        else:
            raise ValueError(f"Unsupported type for time_attr: {type(value)}")

    @override
    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> T:
        """create an instance of the Element or its subclass"""
        if "lion_class" in data:
            cls = get_class(class_name=data.pop("lion_class"))
        if cls.from_dict.__func__ != Element.from_dict.__func__:
            return cls.from_dict(data, **kwargs)
        return cls.model_validate(data, **kwargs)

    @override
    def to_dict(self, **kwargs: Any) -> dict:
        """Convert the Element to a dictionary representation."""
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
        """Always True"""
        return True

    def __len__(self) -> int:
        """Return the length of the Element."""
        return 1


__all__ = ["Element"]

# File: lion_core/generic/element.py
