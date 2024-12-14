# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from collections.abc import Callable

from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    create_model,
    field_validator,
    model_validator,
)
from pydantic.fields import FieldInfo
from typing_extensions import Self

from lionagi.libs.parse.types import validate_boolean
from lionagi.utils import copy

from ..protocols.models import BaseSchemaModel
from .models import FieldModel

__all__ = ("ModelParams",)


class ModelParams(BaseSchemaModel):
    """
    Configuration class for dynamic Pydantic model generation.
    Manages field definitions, validators, inheritance, and model metadata.

    Attributes:
        name: Model class name, defaults to base class name if not specified
        parameter_fields: Field definitions as {name: FieldInfo} mapping
        base_type: Base class for model inheritance, defaults to BaseModel
        field_models: List of field model definitions with validators
        exclude_fields: Fields to exclude from final model
        field_descriptions: Field documentation as {name: description} mapping
        inherit_base: Whether to inherit from base_type, defaults to True
        config_dict: Model configuration options
        doc: Model class docstring
        frozen: Whether model should be immutable
    """

    name: str | None = None
    parameter_fields: dict[str, FieldInfo] = Field(default_factory=dict)
    base_type: type[BaseModel] = Field(default=BaseModel)
    field_models: list[FieldModel] = Field(default_factory=list)
    exclude_fields: list = Field(default_factory=list)
    field_descriptions: dict = Field(default_factory=dict)
    inherit_base: bool = Field(default=True)
    config_dict: dict | None = Field(default=None)
    doc: str | None = Field(default=None)
    frozen: bool = False
    _validators: dict[str, Callable] | None = PrivateAttr(default=None)
    _use_keys: set[str] = PrivateAttr(default_factory=set)

    @property
    def use_fields(self):
        """
        Get field definitions for model creation.

        Returns:
            dict: Mapping of field names to (annotation, field_info) tuples.
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
    def validate_parameters(cls, value):
        """Validate field info dictionary structure and types."""
        if value is None:
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
    def validate_base(cls, value) -> type[BaseModel]:
        """Validate base model type is proper Pydantic model class."""
        if value is None:
            return BaseModel
        if isinstance(value, type) and issubclass(value, BaseModel):
            return value
        if isinstance(value, BaseModel):
            return value.__class__
        raise ValueError("Base must be a BaseModel subclass or instance.")

    @field_validator("exclude_fields", mode="before")
    def validate_fields(cls, value) -> list[str]:
        """Validate and normalize excluded fields list."""
        if value is None:
            return []
        if isinstance(value, dict):
            value = list(value.keys())
        if isinstance(value, set | tuple):
            value = list(value)
        if isinstance(value, list):
            if not all(isinstance(i, str) for i in value):
                raise ValueError("Field names must be strings.")
            return copy(value)
        raise ValueError("Fields must be a list, set, or dictionary.")

    @field_validator("field_descriptions", mode="before")
    def validate_field_descriptions(cls, value) -> dict[str, str]:
        """Validate field description dictionary format."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("Field descriptions must be a dictionary.")
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValueError("Field names must be strings.")
            if not isinstance(v, str):
                raise ValueError("Field descriptions must be strings.")
        return value

    @field_validator("inherit_base", mode="before")
    def validate_inherit_base(cls, value) -> bool:
        """Validate and normalize inheritance flag."""
        try:
            return validate_boolean(value)
        except Exception:
            return True

    @field_validator("name", mode="before")
    def validate_name(cls, value) -> str:
        """Validate model name format."""
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        return value

    @field_validator("field_models", mode="before")
    def _validate_field_models(cls, value):
        """Validate field model list contents."""
        if value is None:
            return []
        value = [value] if not isinstance(value, list) else value
        if not all(isinstance(i, FieldModel) for i in value):
            raise ValueError("Field models must be FieldModel objects.")
        return value

    @model_validator(mode="after")
    def validate_param_model(self) -> Self:
        """
        Validate and configure complete model structure.
        Merges base fields, applies exclusions, and sets up validators.
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
        """
        Create new Pydantic model based on configuration.

        Returns:
            type[BaseModel]: New model class with configured fields and validators.
        """

        a: type[BaseModel] = create_model(
            self.name or "StepModel",
            __config__=self.config_dict,
            __doc__=self.doc,
            __base__=self.base_type if self.inherit_base else None,
            __validators__=self._validators,
            **self.use_fields,
        )
        if self.frozen:
            a.model_config["frozen"] = True
        return a


# File: lionagi/protocols/model_params.py
