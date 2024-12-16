# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


"""
Core model classes providing serialization, validation, and auto-field capabilities.
Integrates with Pydantic for robust data handling and validation.
"""

from __future__ import annotations

from collections.abc import Callable, ItemsView, Iterator, ValuesView
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)
from pydantic.fields import FieldInfo
from typing_extensions import override

from lionagi.libs.nested import flatten, nget, ninsert, npop, nset
from lionagi.utils import UNDEFINED, copy, is_same_dtype, to_list

INDICE_TYPE = str | list[str | int]

__all__ = (
    "BaseLionModel",
    "SchemaModel",
    "FieldModel",
    "OperableModel",
    "Note",
)


class BaseLionModel(BaseModel):
    """Base model with serialization and class type preservation."""

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return cls.__name__

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """Convert to dict with class type info."""
        return self.model_dump(**kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseLionModel:
        """Create instance from dict, handling class type."""
        return cls.model_validate(data)


class SchemaModel(BaseLionModel):
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


class FieldModel(SchemaModel):
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


class OperableModel(BaseLionModel):

    extra_fields: dict[str, Any] = Field(default_factory=dict)

    @field_serializer("extra_fields")
    def _serialize_extra_fields(
        self,
        value: dict[str, FieldInfo],
    ) -> dict[str, Any]:
        """Custom serializer for extra fields."""
        output_dict = {}
        for k in value.keys():
            output_dict[k] = self.__dict__.get(k)
        return output_dict

    @field_validator("extra_fields")
    def _validate_extra_fields(
        cls,
        value: list[FieldModel] | dict[str, FieldModel | FieldInfo],
    ) -> dict[str, FieldInfo]:
        out = {}
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, FieldModel):
                    out[k] = v.field_info
                elif isinstance(v, FieldInfo):
                    out[k] = v
            return out

        elif isinstance(value, list) and is_same_dtype(value, FieldModel):
            return {v.name: v.field_info for v in value}

        raise ValueError("Invalid extra_fields value")

    def clean_dump(self) -> dict:
        dict_ = self.model_dump()
        dict_.pop("extra_fields")
        dict_.update(self._serialize_extra_fields(self.extra_fields))
        for k, v in dict_.items():
            if v is UNDEFINED:
                dict_.pop(k)
        return dict_

    def to_dict(self) -> dict:
        dict_ = self.model_dump()
        dict_.pop("extra_fields")
        dict_.update(self._serialize_extra_fields(self.extra_fields))
        return dict_

    @property
    def all_fields(self) -> dict[str, FieldInfo]:
        """
        Get all fields including model fields and extra fields.

        Returns:
            dict[str, FieldInfo]: A dictionary containing all fields.
        """
        a = {**self.model_fields, **self.extra_fields}
        a.pop("extra_fields", None)
        return a

    def add_field(
        self,
        field_name: str,
        /,
        value: Any = UNDEFINED,
        annotation: type = UNDEFINED,
        field_obj: FieldInfo = UNDEFINED,
        field_model: FieldModel = UNDEFINED,
        **kwargs,
    ) -> None:
        """
        Add a new field to the component's extra fields.

        Args:
            field_name: The name of the field to add.
            value: The value of the field.
            annotation: Type annotation for the field.
            field_obj: A pre-configured FieldInfo object.
            **kwargs: Additional keyword arguments for Field configuration.

        Raises:
            LionValueError: If the field already exists.
        """
        if field_name in self.all_fields:
            raise ValueError(f"Field '{field_name}' already exists")

        self.update_field(
            field_name,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            field_model=field_model,
            **kwargs,
        )

    def update_field(
        self,
        field_name: str,
        /,
        value: Any = UNDEFINED,
        annotation: type = None,
        field_obj: FieldInfo = None,
        field_model: FieldModel = None,
        **kwargs,
    ) -> None:
        """
        Update an existing field or create a new one if it doesn't exist.

        Args:
            field_name: The name of the field to update or create.
            value: The new value for the field.
            annotation: Type annotation for the field.
            field_obj: A pre-configured FieldInfo object.
            **kwargs: Additional keyword arguments for Field configuration.

        Raises:
            ValueError: If both 'default' and 'default_factory' are
                        provided in kwargs.
        """

        # pydanitc Field object cannot have both default and default_factory
        if "default" in kwargs and "default_factory" in kwargs:
            raise ValueError(
                "Cannot provide both 'default' and 'default_factory'",
            )

        if field_obj and field_model:
            raise ValueError(
                "Cannot provide both 'field_obj' and 'field_model'",
            )

        # handle field_obj
        if field_obj:
            if not isinstance(field_obj, FieldInfo):
                raise ValueError(
                    "Invalid field_obj, should be a pydantic FieldInfo object"
                )
            self.extra_fields[field_name] = field_obj

        if field_model:
            if not isinstance(field_model, FieldModel):
                raise ValueError(
                    "Invalid field_model, should be a FieldModel object"
                )
            self.extra_fields[field_name] = field_model.field_info

        # handle kwargs
        if kwargs:
            if field_name in self.all_fields:  # existing field
                for k, v in kwargs.items():
                    self.field_setattr(field_name, k, v)
            else:
                self.extra_fields[field_name] = Field(**kwargs)

        # handle no explicit defined field
        if not field_obj and not kwargs:
            if field_name not in self.all_fields:
                self.extra_fields[field_name] = Field()

        field_obj = self.all_fields[field_name]

        # handle annotation
        if annotation is not None:
            field_obj.annotation = annotation
        if not field_obj.annotation:
            field_obj.annotation = Any

        # handle value
        if value is UNDEFINED:
            if getattr(self, field_name, UNDEFINED) is not UNDEFINED:
                value = getattr(self, field_name)

            elif getattr(field_obj, "default") is not PydanticUndefined:
                value = field_obj.default

            elif getattr(field_obj, "default_factory"):
                value = field_obj.default_factory()

        setattr(self, field_name, value)

    # field management methods
    def field_setattr(
        self,
        field_name: str,
        attr: str,
        value: Any,
        /,
    ) -> None:
        """Set the value of a field attribute."""
        all_fields = self.all_fields
        if field_name not in all_fields:
            raise KeyError(f"Field {field_name} not found in object fields.")
        field_obj = all_fields[field_name]
        if hasattr(field_obj, attr):
            setattr(field_obj, attr, value)
        else:
            if not isinstance(field_obj.json_schema_extra, dict):
                field_obj.json_schema_extra = {}
            field_obj.json_schema_extra[attr] = value

    def field_hasattr(
        self,
        field_name: str,
        attr: str,
        /,
    ) -> bool:
        """Check if a field has a specific attribute."""
        all_fields = self.all_fields
        if field_name not in all_fields:
            raise KeyError(f"Field {field_name} not found in object fields.")
        field_obj = all_fields[field_name]
        if hasattr(field_obj, attr):
            return True
        elif isinstance(field_obj.json_schema_extra, dict):
            if field_name in field_obj.json_schema_extra:
                return True
        else:
            return False

    def field_getattr(
        self,
        field_name: str,
        attr: str,
        default: Any = UNDEFINED,
        /,
    ) -> Any:
        """Get the value of a field attribute."""
        all_fields = self.all_fields

        if field_name not in all_fields:
            raise KeyError(f"Field {field_name} not found in object fields.")

        if str(attr).strip("s").lower() == "annotation":
            return self.model_fields[field_name].annotation

        field_obj = all_fields[field_name]

        # check fieldinfo attr
        value = getattr(field_obj, attr, UNDEFINED)
        if value is not UNDEFINED:
            return value
        else:
            if isinstance(field_obj.json_schema_extra, dict):
                value = field_obj.json_schema_extra.get(attr, UNDEFINED)
                if value is not UNDEFINED:
                    return value

        # undefined attr
        if default is not UNDEFINED:
            return default
        else:
            raise AttributeError(
                f"field {field_name} has no attribute {attr}",
            )


class Note(BaseLionModel):
    """A container for managing nested dictionary data structures."""

    content: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize a Note instance with the given keyword arguments."""
        super().__init__()
        self.content = kwargs

    @field_serializer("content")
    def _serialize_content(self, value: Any) -> dict[str, Any]:
        """Serialize the content"""
        output_dict = copy(value, deep=True)
        return output_dict

    def clean_dump(self) -> dict[str, Any]:
        out = copy(self.content)

        for k, v in self.content.items():
            if v is UNDEFINED:
                out.pop(k)
        return out

    def pop(
        self,
        indices: INDICE_TYPE,
        /,
        default: Any = UNDEFINED,
    ) -> Any:
        """Remove and return an item from the nested structure."""
        indices = to_list(indices, flatten=True, dropna=True)
        return npop(self.content, indices, default)

    def insert(self, indices: INDICE_TYPE, value: Any, /) -> None:
        """Insert a value into the nested structure at the specified indice"""
        indices = to_list(indices, flatten=True, dropna=True)
        ninsert(self.content, indices, value)

    def set(self, indices: INDICE_TYPE, value: Any, /) -> None:
        """Set a value in the nested structure at the specified indice"""
        indices = to_list(indices, flatten=True, dropna=True)

        if self.get(indices, None) is None:
            self.insert(indices, value)
        else:
            nset(self.content, indices, value)

    def get(
        self,
        indices: INDICE_TYPE,
        /,
        default: Any = UNDEFINED,
    ) -> Any:
        """Get a value from the nested structure at the specified indice"""
        indices = to_list(indices, flatten=True, dropna=True)
        return nget(self.content, indices, default)

    def keys(self, /, flat: bool = False, **kwargs: Any) -> list:
        """
        Get the keys of the Note.

        Args:
            flat: If True, return flattened keys.
            kwargs: Additional keyword arguments for flattening
        """
        if flat:
            kwargs["coerce_keys"] = kwargs.get("coerce_keys", True)
            kwargs["coerce_sequence"] = kwargs.get("coerce_sequence", "list")
            return flatten(self.content, **kwargs).keys()
        return list(self.content.keys())

    def values(self, /, flat: bool = False, **kwargs: Any) -> ValuesView:
        """
        Get the values of the Note.

        Args:
            flat: If True, return flattened values.
            kwargs: Additional keyword arguments for flattening
        """
        if flat:
            kwargs["coerce_keys"] = kwargs.get("coerce_keys", True)
            kwargs["coerce_sequence"] = kwargs.get("coerce_sequence", "list")
            return flatten(self.content, **kwargs).values()
        return self.content.values()

    def items(self, /, flat: bool = False, **kwargs: Any) -> ItemsView:
        """
        Get the items of the Note.

        Args:
            flat: If True, return flattened items.
            kwargs: Additional keyword arguments for flattening
        """
        if flat:
            kwargs["coerce_keys"] = kwargs.get("coerce_keys", True)
            kwargs["coerce_sequence"] = kwargs.get("coerce_sequence", "list")
            return flatten(self.content, **kwargs).items()
        return self.content.items()

    @override
    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """
        Convert the Note to a dictionary.

        kwargs: Additional keyword arguments for BaseModel.model_dump

        Returns:
            A dictionary representation of the Note.
        """
        output_dict = self.model_dump(**kwargs)
        return output_dict["content"]

    def clear(self) -> None:
        """Clear the content of the Note."""
        self.content.clear()

    def update(
        self,
        indices: INDICE_TYPE,
        value: Any,
    ) -> None:
        existing = None
        if not indices:
            existing = self.content
        else:
            existing = self.get(indices, None)

        if existing is None:
            if not isinstance(value, (list, dict)):
                value = [value]
            self.set(indices, value)

        if isinstance(existing, list):
            if isinstance(value, list):
                existing.extend(value)
            else:
                existing.append(value)

        elif isinstance(existing, dict):
            if isinstance(value, self.__class__):
                value = value.content

            if isinstance(value, dict):
                existing.update(value)
            else:
                raise ValueError(
                    "Cannot update a dictionary with a non-dictionary value."
                )

    @override
    @classmethod
    def from_dict(cls, kwargs: Any) -> Note:
        """Create a Note from a dictionary."""
        return cls(**kwargs)

    def __contains__(self, indices: INDICE_TYPE) -> bool:
        """Check if the Note contains the specified indices."""
        return self.content.get(indices, UNDEFINED) is not UNDEFINED

    def __len__(self) -> int:
        """Return the length of the Note's content."""
        return len(self.content)

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the Note's content."""
        return iter(self.content)

    def __next__(self) -> str:
        """Return the next item in the Note's content."""
        return next(iter(self.content))

    @override
    def __str__(self) -> str:
        """Return a string representation of the Note's content."""
        return str(self.content)

    @override
    def __repr__(self) -> str:
        """Return a detailed string representation of the Note's content."""
        return repr(self.content)

    def __getitem__(self, indices: INDICE_TYPE) -> Any:
        """Get an item from the Note using index notation."""
        indices = to_list(indices, flatten=True, dropna=True)
        return self.get(indices)

    def __setitem__(self, indices: INDICE_TYPE, value: Any) -> None:
        """Set an item in the Note using index notation."""
        self.set(indices, value)
