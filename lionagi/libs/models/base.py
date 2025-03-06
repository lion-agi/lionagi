# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from collections.abc import Callable
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    create_model,
    field_validator,
    model_validator,
)
from pydantic.fields import FieldInfo
from typing_extensions import Self

from lionagi.libs.validate.common_field_validators import (
    validate_boolean_field,
    validate_callable,
    validate_dict_kwargs_params,
    validate_list_dict_str_keys,
    validate_model_to_type,
    validate_nullable_string_field,
    validate_same_dtype_flat_list,
    validate_str_str_dict,
)
from lionagi.utils import UNDEFINED, HashableModel, UndefinedType, copy


class SchemaModel(HashableModel):

    model_config = ConfigDict(
        extra="forbid",
        validate_default=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    @classmethod
    def keys(cls) -> list[str]:
        """Get list of model field names.

        Returns:
            List of field names defined in model schema
        """
        return list(cls.model_fields.keys())


class FieldModel(SchemaModel):
    """Model for defining and configuring Pydantic field attributes.

    This class provides a structured way to define fields with comprehensive
    configuration options including type validation, default values, documentation,
    and validation rules.
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
        return validate_dict_kwargs_params(cls, value)

    @field_validator("validator", mode="before")
    def _validate_field_validator(cls, value) -> Callable | Any:
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
        if (
            self.default is not UNDEFINED
            and self.default_factory is not UNDEFINED
        ):
            raise ValueError("Cannot have both default and default_factory")
        return self


class ModelParams(SchemaModel):
    """Configuration class for dynamically creating new Pydantic models.

    This class provides a flexible way to create Pydantic models with customizable
    fields, validators, and configurations. It supports inheritance from base
    models, field exclusion, and custom validation rules.

    Args:
        name: Name for the generated model class.
        parameter_fields: Field definitions for the model.
        base_type: Base model class to inherit from.
        field_models: List of field model definitions.
        exclude_fields: Fields to exclude from the final model.
        field_descriptions: Custom descriptions for fields.
        inherit_base: Whether to inherit from base_type.
        config_dict: Pydantic model configuration.
        doc: Docstring for the generated model.
        frozen: Whether the model should be immutable.
    """

    name: str | None = Field(
        default=None, description="Name for the generated model class"
    )

    parameter_fields: dict[str, FieldInfo] = Field(
        default_factory=dict, description="Field definitions for the model"
    )

    base_type: type[BaseModel] = Field(
        default=BaseModel, description="Base model class to inherit from"
    )

    field_models: list[FieldModel] = Field(
        default_factory=list, description="List of field model definitions"
    )

    exclude_fields: list = Field(
        default_factory=list,
        description="Fields to exclude from the final model",
    )

    field_descriptions: dict = Field(
        default_factory=dict, description="Custom descriptions for fields"
    )

    inherit_base: bool = Field(
        default=True, description="Whether to inherit from base_type"
    )

    config_dict: dict | None = Field(
        default=None, description="Pydantic model configuration"
    )

    doc: str | None = Field(
        default=None, description="Docstring for the generated model"
    )

    frozen: bool = Field(
        default=False, description="Whether the model should be immutable"
    )
    _validators: dict[str, Callable] | None = PrivateAttr(default=None)
    _use_keys: set[str] = PrivateAttr(default_factory=set)

    @property
    def use_fields(self) -> dict[str, tuple[type, FieldInfo]]:
        """Get field definitions to use in new model.

        Filters and combines fields from parameter_fields and field_models based on
        the _use_keys set, preparing them for use in model creation.

        Returns:
            A dictionary mapping field names to tuples of (type, FieldInfo),
            containing only the fields that should be included in the new model.
        """
        params = {
            k: v
            for k, v in self.parameter_fields.items()
            if k in self._use_keys
        }
        params.update(
            {
                f.name: f.field_info
                for f in self.field_models
                if f.name in self._use_keys
            }
        )
        return {k: (v.annotation, v) for k, v in params.items()}

    @field_validator("parameter_fields", mode="before")
    def _validate_parameters(cls, value) -> dict[str, FieldInfo]:
        if value in [None, {}, []]:
            return {}
        if not isinstance(value, dict):
            raise ValueError("Fields must be a dictionary.")
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValueError("Field names must be strings.")
            if not isinstance(v, FieldInfo):
                raise ValueError("Field values must be FieldInfo objects.")
        return copy(value)

    @field_validator("base_type", mode="before")
    def _validate_base(cls, value) -> type[BaseModel]:
        return validate_model_to_type(cls, value)

    @field_validator("exclude_fields", mode="before")
    def _validate_fields(cls, value) -> list[str]:
        return validate_list_dict_str_keys(cls, value)

    @field_validator("field_descriptions", mode="before")
    def _validate_field_descriptions(cls, value) -> dict[str, str]:
        return validate_str_str_dict(cls, value)

    @field_validator("inherit_base", mode="before")
    def _validate_inherit_base(cls, value) -> bool:
        return validate_boolean_field(cls, value, default=True)

    @field_validator("name", mode="before")
    def _validate_name(cls, value) -> str | None:
        return validate_nullable_string_field(cls, value, field_name="Name")

    @field_validator("field_models", mode="before")
    def _validate_field_models(cls, value) -> list[FieldModel]:
        return validate_same_dtype_flat_list(cls, value, FieldModel)

    @model_validator(mode="after")
    def validate_param_model(self) -> Self:
        """Validate complete model configuration.

        Performs comprehensive validation and setup of the model parameters:
        1. Updates parameter fields from base type if present
        2. Merges field models into parameter fields
        3. Manages field inclusion/exclusion via _use_keys
        4. Sets up validators from field models
        5. Applies field descriptions
        6. Handles model name resolution

        Returns:
            The validated model instance with all configurations applied.
        """
        if self.base_type is not None:
            self.parameter_fields.update(copy(self.base_type.model_fields))

        self.parameter_fields.update(
            {f.name: f.field_info for f in self.field_models}
        )

        use_keys = list(self.parameter_fields.keys())
        use_keys.extend(list(self._use_keys))

        if self.exclude_fields:
            use_keys = [i for i in use_keys if i not in self.exclude_fields]

        self._use_keys = set(use_keys)

        validators = {}

        for i in self.field_models:
            if i.field_validator is not None:
                validators.update(i.field_validator)
        self._validators = validators

        if self.field_descriptions:
            for i in self.field_models:
                if i.name in self.field_descriptions:
                    i.description = self.field_descriptions[i.name]

        if not isinstance(self.name, str):
            if hasattr(self.base_type, "class_name"):
                if callable(self.base_type.class_name):
                    self.name = self.base_type.class_name()
                else:
                    self.name = self.base_type.class_name
            elif inspect.isclass(self.base_type):
                self.name = self.base_type.__name__

        return self

    def create_new_model(self) -> type[BaseModel]:
        """Create new Pydantic model with specified configuration."""
        base_type = self.base_type if self.inherit_base else None

        if base_type and self.exclude_fields:
            if any(
                i in self.exclude_fields for i in self.base_type.model_fields
            ):
                base_type = None

        a: type[BaseModel] = create_model(
            self.name or "StepModel",
            __config__=self.config_dict,
            __doc__=self.doc,
            __base__=base_type,
            __validators__=self._validators,
            **self.use_fields,
        )
        if self.frozen:
            a.model_config["frozen"] = True
        return a
