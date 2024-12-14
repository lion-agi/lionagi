from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import ConfigDict, Field, field_validator
from pydantic.fields import FieldInfo

from lionagi.protocols.models import BaseSchemaModel
from lionagi.utils import UNDEFINED


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
    validators: list | Callable = UNDEFINED
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
