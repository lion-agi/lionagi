# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from collections.abc import Callable
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    create_model,
    field_validator,
    model_validator,
)
from pydantic.fields import FieldInfo

from lionagi.libs.validate.common_field_validators import (
    validate_boolean_field,
    validate_list_dict_str_keys,
    validate_model_to_type,
    validate_nullable_string_field,
    validate_same_dtype_flat_list,
    validate_str_str_dict,
)
from lionagi.utils import copy

from .field_model import FieldModel
from .schema_model import SchemaModel

__all__ = ("ModelParams",)


class ModelParams(SchemaModel):
    """Configuration class for dynamically creating new Pydantic models.

    This class provides a flexible way to create Pydantic models with customizable
    fields, validators, and configurations. It supports inheritance from base
    models, field exclusion, and custom validation rules.

    Attributes:
        name (str | None): Name for the generated model class.
        parameter_fields (dict[str, FieldInfo]): Field definitions for the model.
        base_type (type[BaseModel]): Base model class to inherit from.
        field_models (list[FieldModel]): List of field model definitions.
        exclude_fields (list): Fields to exclude from the final model.
        field_descriptions (dict): Custom descriptions for fields.
        inherit_base (bool): Whether to inherit from base_type.
        config_dict (dict | None): Pydantic model configuration.
        doc (str | None): Docstring for the generated model.
        frozen (bool): Whether the model should be immutable.
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

        Returns:
            dict[str, tuple[type, FieldInfo]]: Mapping of field names to their
            type and field info.
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
        """Validate parameter field definitions.

        Args:
            value: Value to validate.

        Returns:
            dict[str, FieldInfo]: Validated parameter fields.

        Raises:
            ValueError: If parameter fields are invalid.
        """
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
        """Validate base model type.

        Args:
            value: Value to validate.

        Returns:
            type[BaseModel]: Validated base model type.

        Raises:
            ValueError: If base type is invalid.
        """
        return validate_model_to_type(cls, value)

    @field_validator("exclude_fields", mode="before")
    def _validate_fields(cls, value) -> list[str]:
        """Validate excluded fields list.

        Args:
            value: Value to validate.

        Returns:
            list[str]: Validated list of field names to exclude.

        Raises:
            ValueError: If field names are invalid.
        """
        return validate_list_dict_str_keys(cls, value)

    @field_validator("field_descriptions", mode="before")
    def _validate_field_descriptions(cls, value) -> dict[str, str]:
        """Validate field descriptions dictionary.

        Args:
            value: Value to validate.

        Returns:
            dict[str, str]: Validated field descriptions.

        Raises:
            ValueError: If descriptions are invalid.
        """
        return validate_str_str_dict(cls, value)

    @field_validator("inherit_base", mode="before")
    def _validate_inherit_base(cls, value) -> bool:
        """Validate inherit_base flag.

        Args:
            value: Value to validate.

        Returns:
            bool: Validated inherit_base value.
        """
        return validate_boolean_field(cls, value, default=True)

    @field_validator("name", mode="before")
    def _validate_name(cls, value) -> str | None:
        """Validate model name.

        Args:
            value: Value to validate.

        Returns:
            str | None: Validated model name.

        Raises:
            ValueError: If name is invalid.
        """
        return validate_nullable_string_field(cls, value, field_name="Name")

    @field_validator("field_models", mode="before")
    def _validate_field_models(cls, value) -> list[FieldModel]:
        """Validate field model definitions.

        Args:
            value: Value to validate.

        Returns:
            list[FieldModel]: Validated field models.

        Raises:
            ValueError: If field models are invalid.
        """

        return validate_same_dtype_flat_list(cls, value, FieldModel)

    @model_validator(mode="after")
    def validate_param_model(self) -> Self:
        """Validate complete model configuration.

        This method performs final validation and setup of the model parameters,
        including updating field definitions, validators, and descriptions.

        Returns:
            Self: The validated instance.
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
        """Create new Pydantic model with specified configuration.

        This method generates a new Pydantic model class based on the configured
        parameters, including fields, validators, and inheritance settings.

        Returns:
            type[BaseModel]: Newly created Pydantic model class.
        """
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
