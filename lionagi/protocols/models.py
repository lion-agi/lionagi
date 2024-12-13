# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


"""
Core model classes providing serialization, validation, and auto-field capabilities.
Integrates with Pydantic for robust data handling and validation.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)
from pydantic.fields import FieldInfo

from lionagi.utils import UNDEFINED

from .base import ID, IDType, Observable

LION_CLASS_REGISTRY: dict[str, type[BaseLionModel]] = {}


__all__ = (
    "BaseLionModel",
    "BaseSchemaModel",
    "BaseAutoModel",
    "FieldModel",
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
        data.pop("lion_class", None)
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


class FieldModel(BaseSchemaModel):
    """Configuration model for dynamic field creation.

    Provides comprehensive field configuration including:
    - Basic field attributes (name, type, defaults)
    - Documentation (title, description, examples)
    - Validation rules and custom validators
    - Serialization options
    """

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    # Field configuration attributes
    default: Any = UNDEFINED
    default_factory: Callable = UNDEFINED
    title: str = UNDEFINED
    description: str = UNDEFINED
    examples: list = UNDEFINED
    validators: list = UNDEFINED
    exclude: bool = UNDEFINED
    deprecated: bool = UNDEFINED
    frozen: bool = UNDEFINED
    alias: str = UNDEFINED
    alias_priority: int = UNDEFINED

    name: str = Field(
        ...,
        exclude=True,
        description="Field name (required)",
    )
    annotation: type | Any = Field(
        UNDEFINED,
        exclude=True,
        description="Type annotation for the field",
    )
    validator: Callable | Any = Field(
        UNDEFINED,
        exclude=True,
        description="Custom validation function",
    )
    validator_kwargs: dict | Any = Field(
        default_factory=dict,
        exclude=True,
        description="Configuration for validator",
    )

    @property
    def field_info(self) -> FieldInfo:
        """Generate Pydantic field configuration."""
        field_obj: FieldInfo = Field(**self.model_dump(exclude_unset=True))  # type: ignore
        field_obj.annotation = (
            self.annotation if self.annotation is not UNDEFINED else Any
        )
        return field_obj

    @property
    def field_validator(self) -> dict[str, Callable] | None:
        """Generate validator configuration if set."""
        if self.validator is UNDEFINED:
            return None
        kwargs = self.validator_kwargs or {}
        return {
            f"{self.name}_validator": field_validator(self.name, **kwargs)(
                self.validator
            )
        }
