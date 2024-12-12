# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from attr import dataclass
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
    "ValidatorConfig",
    "FieldModel",
)


def get_class(class_name: str) -> type[BaseLionModel]:
    """Retrieve a class by name from the registry.

    Args:
        class_name: The name of the class to retrieve.

    Returns:
        The class object associated with `class_name`.

    Raises:
        ValueError: If no class is registered under `class_name`.
    """
    if class_name not in LION_CLASS_REGISTRY:
        raise ValueError(f"No registered Lion class found for '{class_name}'.")
    return LION_CLASS_REGISTRY[class_name]


class BaseLionModel(BaseModel):
    """Base model providing core serialization capabilities.

    Extends Pydantic BaseModel with:
      - Class type preservation (via `lion_class` field in serialization).
      - Enhanced serialization and deserialization.

    Serves as the foundation for the Lion model hierarchy.
    """

    @classmethod
    def class_name(cls) -> str:
        """Get the class name.

        Returns:
            str: The name of this class.
        """
        return cls.__name__

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary, including class type information.

        Returns:
            A dictionary representation of the model, including a 'lion_class'
            field for type preservation.
        """
        dict_ = self.model_dump()
        dict_["lion_class"] = self.class_name()
        return dict_

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseLionModel:
        """Create a model instance from a dictionary.

        Args:
            data: A dictionary containing model data.

        Returns:
            An instance of the model class.

        Note:
            If 'lion_class' is present in `data`, it is removed before instantiation.
        """
        data.pop("lion_class", None)
        return cls(**data)


class BaseSchemaModel(BaseLionModel):
    """Schema model with strict validation.

    Provides a base for schema models with:
      - Strict field validation (no extra fields).
      - Arbitrary types allowed if configured.
      - Enum values used directly.

    Useful for defining strict input/output schemas.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_default=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    @classmethod
    def keys(cls) -> list[str]:
        """Get a list of model field names.

        Returns:
            A list of field names defined in this model.
        """
        return list(cls.model_fields.keys())


class BaseAutoModel(BaseLionModel, Observable):
    """A full-featured model with automatic fields and validation.

    Adds:
      - Automatic unique ID generation (via `id` field).
      - Timestamp tracking (via `created_timestamp`).
      - Optional embedding vector storage.
      - Strict field handling.

    Attributes:
        id: Unique identifier for this element, frozen after creation.
        created_timestamp: Creation time as a Unix timestamp, frozen after creation.
        embedding: Optional embedding vector as a list of floats.
    """

    id: IDType = Field(
        default_factory=ID.generate,
        title="Lion ID",
        description="Unique identifier for the element",
        frozen=True,
    )

    @field_serializer("id")
    def _serialize_id(self, value: IDType) -> str:
        """Convert ID to a string.

        Args:
            value: The ID to serialize.

        Returns:
            The string representation of the ID.
        """
        return str(value)

    @field_validator("id", mode="before")
    @classmethod
    def _validate_id(cls, value: IDType) -> str:
        """Validate and normalize the ID format.

        Args:
            value: The raw ID value to validate.

        Returns:
            A validated ID string.

        Raises:
            ValueError: If the ID format or type is invalid.
        """
        try:
            return ID.get_id(value)
        except Exception:
            raise ValueError(f"Invalid lion id: {value}")

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

    @field_validator("created_timestamp", mode="before")
    @classmethod
    def _validate_created_timestamp(cls, value: Any) -> float:
        """Convert and validate the `created_timestamp` field.

        Args:
            value: The timestamp value to validate. Can be:
                   - float/int: Used directly as a timestamp
                   - datetime: Converted to a timestamp
                   - str: Parsed as float or ISO formatted datetime string

        Returns:
            A float representing the Unix timestamp.

        Raises:
            ValueError: If the timestamp format is invalid.
        """
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
        """Get the creation time as a datetime object.

        Returns:
            A datetime object representing the creation time.
        """
        return datetime.fromtimestamp(self.created_timestamp)

    def __hash__(self) -> int:
        """Hash based on the ID.

        Returns:
            int: The hash of the ID.
        """
        return hash(self.id)

    def __bool__(self) -> bool:
        """Model instances are always considered True.

        Returns:
            True
        """
        return True

    def __len__(self) -> int:
        """Return a fixed size (1).

        Returns:
            int: Always 1.
        """
        return 1

    def __str__(self) -> str:
        """String representation of the model.

        Returns:
            A string showing class name, a prefix of the ID, and creation time.
        """
        timestamp_str = self.created_datetime.isoformat(timespec="minutes")
        return f"{self.class_name()}(id={str(self.id)[:6]}.., timestamp={timestamp_str})"


@dataclass
class ValidatorConfig:
    func: Callable[[Any], Any]
    mode: str | None = None
    kwargs: dict[str, Any] = {}


class FieldModel(BaseSchemaModel):
    """Enhanced field definition model for Lion framework.

    Extends BaseSchemaModel to provide comprehensive field configuration and
    validation capabilities. Allows dynamic field creation with extensive
    configuration options.

    Configuration:
        - Allows extra fields
        - Skips default validation
        - Supports field name aliases
        - Allows arbitrary types
        - Uses enum values

    Attributes:
        Field Configuration:
            default: Default value for the field
            default_factory: Function to generate default value
            title: Field title for documentation
            description: Detailed field description
            examples: Example values for documentation
            validators: List of validation functions
            exclude: Whether to exclude from serialization
            deprecated: Whether field is deprecated
            frozen: Whether field is immutable
            alias: Alternative field name
            alias_priority: Priority for alias resolution

        Core Attributes:
            name: Field name (required)
            annotation: Type annotation
            validator: Custom validation function
            validator_kwargs: Validator configuration

    Examples:
        >>> field = FieldModel(
        ...     name="age",
        ...     annotation=int,
        ...     title="User Age",
        ...     description="Age of the user in years",
        ...     default=0,
        ...     validator=lambda x: x >= 0,
        ...     validator_kwargs={"pre": True}
        ... )
        >>> field_info = field.field_info  # Get Pydantic FieldInfo
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

    # Core field attributes
    name: str = Field(
        ...,  # Required
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
        """Generate Pydantic FieldInfo from current configuration.

        Creates a FieldInfo instance using the current field configuration,
        including all set attributes and validation settings.

        Returns:
            FieldInfo: Configured Pydantic field information

        Note:
            Unset attributes are excluded from the field info to allow
            Pydantic's default handling.
        """
        field_obj: FieldInfo = Field(**self.model_dump(exclude_unset=True))  # type: ignore
        field_obj.annotation = (
            self.annotation if self.annotation is not UNDEFINED else Any
        )
        return field_obj

    @property
    def field_validator(self) -> dict[str, Callable] | None:
        """Generate validator configuration if validator is set.

        Creates a validator configuration dictionary using the current
        validator and its kwargs. The validator is named using the field
        name pattern.

        Returns:
            dict[str, Callable] | None: Validator configuration dictionary
                if validator is set, None otherwise

        Note:
            Validator name is formatted as '{field_name}_validator'
        """
        if self.validator is UNDEFINED:
            return None
        kwargs = self.validator_kwargs or {}
        return {
            f"{self.name}_validator": field_validator(self.name, **kwargs)(
                self.validator
            )
        }
