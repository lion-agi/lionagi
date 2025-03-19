# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from typing import Any

from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic.fields import FieldInfo
from typing_extensions import Self

from lionagi.libs.validate.common_field_validators import (
    validate_callable,
    validate_dict_kwargs_params,
)
from lionagi.utils import UNDEFINED, UndefinedType

from .schema_model import SchemaModel

__all__ = ("FieldModel",)


class FieldModel(SchemaModel):
    """Model for defining and configuring Pydantic field attributes.

    This class provides a structured way to define fields with comprehensive
    configuration options including type validation, default values, documentation,
    and validation rules.

    Args:
        name: Required field identifier.
        annotation: Field type annotation. Defaults to Any.
        default: Default value for the field.
        default_factory: Function to generate default values.
        validator: Optional validation function.
        validator_kwargs: Parameters for validator configuration.
        title: Human-readable field title.
        description: Detailed field description.
        examples: Example values for documentation.
        exclude: Whether to exclude from serialization.
        deprecated: Whether the field is deprecated.
        frozen: Whether the field is immutable.
        alias: Alternative field name.
        alias_priority: Priority for alias resolution.

    Examples:
        >>> field = FieldModel(
        ...     name="age",
        ...     annotation=int,
        ...     default=0,
        ...     description="User age in years",
        ...     validator=lambda cls, v: v if v >= 0 else 0
        ... )
    """

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    # Required core attributes
    name: str | UndefinedType = Field(
        ...,
        description="Field identifier, used as attribute name",
        exclude=True,
    )

    annotation: type | Any = Field(
        default=UNDEFINED,
        description="Type annotation for the field",
        exclude=True,
    )

    validator: Callable | Any = Field(
        default=UNDEFINED,
        description="Optional validation function",
        exclude=True,
    )

    validator_kwargs: dict | None = Field(
        default_factory=dict,
        description="Configuration for validator decorator",
        exclude=True,
    )

    # Field configuration
    default: Any = Field(
        default=UNDEFINED, description="Default value for the field"
    )

    default_factory: Callable | UndefinedType = Field(
        default=UNDEFINED, description="Function to generate default values"
    )

    title: str | UndefinedType = Field(
        default=UNDEFINED, description="Human-readable field title"
    )

    description: str | UndefinedType = Field(
        default=UNDEFINED, description="Detailed field description"
    )

    examples: list | UndefinedType = Field(
        default=UNDEFINED, description="Example values for documentation"
    )

    exclude: bool | UndefinedType = Field(
        default=UNDEFINED, description="Whether to exclude from serialization"
    )

    deprecated: bool | UndefinedType = Field(
        default=UNDEFINED, description="Whether the field is deprecated"
    )

    frozen: bool | UndefinedType = Field(
        default=UNDEFINED, description="Whether the field is immutable"
    )

    alias: str | UndefinedType = Field(
        default=UNDEFINED, description="Alternative field name"
    )

    alias_priority: int | UndefinedType = Field(
        default=UNDEFINED, description="Priority for alias resolution"
    )

    @field_validator("validator_kwargs", mode="before")
    def _validate_validator_kwargs(cls, value):
        """Validate validator kwargs.

        Args:
            value: Validator kwargs to validate.

        Returns:
            Validated kwargs dictionary.
        """
        return validate_dict_kwargs_params(cls, value)

    @field_validator("validator", mode="before")
    def _validate_field_validator(cls, value) -> Callable | Any:
        """Validate field validator function.

        Args:
            value: Validator function to check.

        Returns:
            Validated validator function.

        Raises:
            ValueError: If validator is not callable.
        """
        return validate_callable(cls, value)

    @property
    def field_info(self) -> FieldInfo:
        """Generate Pydantic FieldInfo from current configuration.

        Converts the current field configuration into a Pydantic FieldInfo object,
        handling annotation defaults and field attributes.

        Returns:
            Configured Pydantic FieldInfo object.
        """
        annotation = (
            self.annotation if self.annotation is not UNDEFINED else Any
        )
        field_obj = Field(**self.to_dict())  # type: ignore
        field_obj.annotation = annotation
        return field_obj

    @property
    def field_validator(self) -> dict[str, Callable] | None:
        """Create field validator configuration.

        Generates a validator configuration dictionary if a validator function
        is defined, otherwise returns None.

        Returns:
            Dictionary mapping validator name to validator function if defined,
            None otherwise.
        """
        if self.validator is UNDEFINED:
            return None
        kwargs = self.validator_kwargs or {}
        return {
            f"{self.name}_validator": field_validator(self.name, **kwargs)(
                self.validator
            )
        }

    @model_validator(mode="after")
    def _validate_defaults(self) -> Self:
        """Ensure default value configuration is valid.

        Validates that default and default_factory are not both set, as this
        would create ambiguity about which default to use.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If both default and default_factory are set.
        """
        if (
            self.default is not UNDEFINED
            and self.default_factory is not UNDEFINED
        ):
            raise ValueError("Cannot have both default and default_factory")
        return self
