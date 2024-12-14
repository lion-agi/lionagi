# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


"""
Core model classes providing serialization, validation, and auto-field capabilities.
Integrates with Pydantic for robust data handling and validation.
"""

from __future__ import annotations

from datetime import datetime
from os import name
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from .base import ID, IDType, Observable

LION_CLASS_REGISTRY: dict[str, type[BaseLionModel]] = {}


__all__ = (
    "BaseLionModel",
    "BaseSchemaModel",
    "BaseAutoModel",
)


def get_class(class_name: str) -> type[BaseLionModel]:
    """Get registered model class by name."""
    if class_name not in LION_CLASS_REGISTRY:
        raise ValueError(f"No registered Lion class found for '{class_name}'.")
    return LION_CLASS_REGISTRY[class_name]


class BaseLionModel(BaseModel):
    """Base model with serialization and class type preservation."""

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return cls.__name__

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict with class type info."""
        dict_ = self.model_dump()
        dict_["lion_class"] = self.class_name()
        return dict_

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseLionModel:
        """Create instance from dict, handling class type."""
        if "lion_class" in data:
            data.pop("lion_class")
        return cls(**data)


class BaseSchemaModel(BaseLionModel):
    """Schema model with strict validation and arbitrary type support."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    @classmethod
    def keys(cls) -> list[str]:
        """Get model field names."""
        return list(cls.model_fields.keys())


class BaseAutoModel(BaseLionModel, Observable):
    """Model with auto ID, timestamp tracking and validation.

    Features:
    - Auto ID generation
    - Creation timestamp
    - Field validation
    - String representation
    """

    id: IDType = Field(
        default_factory=ID.generate,
        title="Lion ID",
        description="Unique identifier for the element",
        frozen=True,
    )

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    created_timestamp: float = Field(
        default_factory=lambda: datetime.now().timestamp(),
        title="Creation Timestamp",
        frozen=True,
    )

    def __init_subclass__(cls, **kwargs):
        """Register class in the global registry."""
        if cls.class_name() not in LION_CLASS_REGISTRY:
            LION_CLASS_REGISTRY[cls.class_name()] = cls

        return super().__init_subclass__(**kwargs)

    @field_serializer("id")
    def _serialize_id(self, value: IDType) -> str:
        """Serialize ID to string."""
        return str(value)

    @field_validator("id", mode="before")
    @classmethod
    def _validate_id(cls, value: IDType) -> str:
        """Validate ID format."""
        try:
            return ID.get_id(value)
        except Exception:
            raise ValueError(f"Invalid lion id: {value}")

    @field_validator("created_timestamp", mode="before")
    @classmethod
    def _validate_created_timestamp(cls, value: Any) -> float:
        """Validate and convert timestamp from multiple formats."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, datetime):
            return value.timestamp()

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                # Attempt ISO format parsing
                try:
                    return datetime.fromisoformat(value).timestamp()
                except Exception:
                    raise ValueError(
                        f"Invalid datetime string format: {value}"
                    ) from None

        raise ValueError(f"Invalid timestamp value: {value}")

    @property
    def created_datetime(self) -> datetime:
        """Get creation time as datetime."""
        return datetime.fromtimestamp(self.created_timestamp)

    @classmethod
    def from_dict(cls, data: dict) -> BaseAutoModel:
        """Create instance from dict, handling class type."""
        if "lion_class" in data:
            lion_class = get_class(data.pop("lion_class"))
            if lion_class.from_dict != BaseAutoModel.from_dict:
                data = {
                    k: v
                    for k, v in data.items()
                    if k in lion_class.model_fields
                }
                return lion_class.from_dict(data)
        return cls.model_validate(
            {k: v for k, v in data.items() if k in cls.model_fields}
        )

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __bool__(self) -> bool:
        """Always True."""
        return True

    def __len__(self) -> int:
        """Fixed size of 1."""
        return 1

    def __str__(self) -> str:
        """Short string with ID prefix and creation time."""
        timestamp_str = self.created_datetime.isoformat(timespec="minutes")
        return f"{self.class_name()}(id={str(self.id)[:6]}.., timestamp={timestamp_str})"

    def __repr__(self) -> str:
        """Full representation with complete ID."""
        return f"{self.class_name()}(id={self.id}, timestamp={self.created_datetime})"
