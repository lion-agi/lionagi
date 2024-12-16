# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, ClassVar, TypeVar

from pydantic import Field, field_serializer
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from typing_extensions import override

from lionagi._class_registry import get_class
from lionagi.utils import UNDEFINED, copy, time

from .adapter import Adapter, AdapterRegistry, ComponentRegistry
from .element import Element
from .models import FieldModel, Note, OperableModel

FIELD_NAME = TypeVar("FIELD_NAME", bound=str)

DEFAULT_SERIALIZATION_INCLUDE: set[str] = {
    "id",
    "timestamp",
    "metadata",
    "content",
    "embedding",
}

__all__ = ("Component",)


class Component(Element, OperableModel):
    """Extended base class for components in the Lion framework."""

    metadata: Note = Field(
        default_factory=Note,
        description="Additional metadata for the component",
    )

    content: Any = Field(
        default=None,
        description="The main content of the Component",
    )

    embedding: list[float] = Field(default_factory=list)

    _adapter_registry: ClassVar = ComponentRegistry

    @field_serializer("metadata")
    def _serialize_metadata(self, value: Note):
        return value.to_dict()

    def add_field(
        self,
        field_name: FIELD_NAME,
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

    # when updating field, we do not check the validity of annotation
    # meaning current value will not get validated, and can lead to
    # errors when storing and loading if you change annotation to a type
    # that is not compatible with the current value
    def update_field(
        self,
        field_name: FIELD_NAME,
        /,
        value: Any = UNDEFINED,
        annotation: type = UNDEFINED,
        field_obj: FieldInfo = UNDEFINED,
        field_model: FieldModel = UNDEFINED,
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
        super().update_field(
            field_name,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            field_model=field_model,
            **kwargs,
        )
        self._add_last_update(field_name)

    def _add_last_update(self, field_name: FIELD_NAME, /) -> None:
        current_time = time()
        self.metadata.set(["last_updated", field_name], current_time)

    @override
    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """
        Convert the component to a dictionary representation.

        Args:
            **kwargs: Additional arguments to pass to model_dump.

        Returns:
            dict[str, Any]: A dictionary representation of the component.
        """
        dict_ = self.model_dump(**kwargs)
        if isinstance(self.content, Note):
            dict_["content"] = self.content.content
        extra_fields = dict_.pop("extra_fields", {})
        dict_ = {**dict_, **extra_fields, "lion_class": self.class_name()}
        for i in list(dict_.keys()):
            if dict_[i] is UNDEFINED:
                dict_.pop(i)
        return dict_

    def to_note(self, **kwargs: Any) -> Note:
        return Note(**self.to_dict(**kwargs))

    @override
    @classmethod
    def from_dict(cls, data: dict[str, Any], /, **kwargs: Any) -> "Component":
        """
        Create a component instance from a dictionary.

        Args:
            data: The dictionary containing component data.
            **kwargs: Additional arguments for Pydantic model validation.

        Returns:
            T: An instance of the Component class or its subclass.
        """
        input_data = copy(data)
        if "lion_class" in input_data:
            cls = get_class(input_data.pop("lion_class"))
        if cls.from_dict.__func__ != Component.from_dict.__func__:
            return cls.from_dict(input_data, **kwargs)

        extra_fields = {}
        for k, v in list(input_data.items()):
            if k not in cls.model_fields:
                extra_fields[k] = input_data.pop(k)
        obj = cls.model_validate(input_data, **kwargs)
        for k, v in extra_fields.items():
            obj.update_field(k, value=v)

        metadata = copy(data.get("metadata", {}))
        last_updated = metadata.get("last_updated", None)
        if last_updated is not None:
            obj.metadata.set(["last_updated"], last_updated)
        else:
            obj.metadata.pop(["last_updated"], None)
        return obj

    @override
    def __setattr__(self, field_name: str, value: Any) -> None:
        if field_name == "metadata":
            raise AttributeError("Cannot directly assign to metadata.")
        elif field_name == "extra_fields":
            raise AttributeError("Cannot directly assign to extra_fields")
        if field_name in self.extra_fields:
            object.__setattr__(self, field_name, value)
        else:
            super().__setattr__(field_name, value)

        self._add_last_update(field_name)

    @override
    def __getattr__(self, field_name: str) -> Any:
        if field_name in self.extra_fields:
            default_ = self.extra_fields[field_name].default
            if default_ is not PydanticUndefined:
                return default_
            return UNDEFINED

        cls_name = self.__class__.__name__
        raise AttributeError(
            f"'{cls_name}' object has no attribute '{field_name}'",
        )

    @override
    def __str__(self) -> str:
        """Return a concise string representation of the component."""
        content_preview = str(self.content)[:50]
        if len(content_preview) == 50:
            content_preview += "..."

        output_str = (
            f"{self.__class__.__name__}("
            f"id={self.id[:8]}..., "
            f"timestamp={str(self.created_datetime)[:-6]}, "
            f"content='{content_preview}', "
            f"metadata_keys={list(self.metadata.keys())}, "
        )

        for i, j in self.model_dump().items():
            if i not in DEFAULT_SERIALIZATION_INCLUDE:
                if isinstance(j, dict):
                    output_str += f"{i}={list(j.keys())}, "
                elif isinstance(j, str):
                    j_preview = j[:50]
                    if len(j_preview) == 50:
                        j_preview = j_preview + "..."
                    output_str += f"{i}={j_preview}, "
                else:
                    output_str += f"{i}={j}, "

        output_str += f"extra_fields_keys={list(self.extra_fields.keys())})"

        return output_str

    @override
    def __repr__(self) -> str:
        """Return a detailed string representation of the component."""

        def truncate_dict(
            d: dict[str, Any], max_items: int = 5, max_str_len: int = 50
        ) -> dict[str, Any]:
            items = list(d.items())[:max_items]
            truncated = {
                k: (
                    v[:max_str_len] + "..."
                    if isinstance(v, str) and len(v) > max_str_len
                    else v
                )
                for k, v in items
            }
            if len(d) > max_items:
                truncated["..."] = f"({len(d) - max_items} more items)"
            return truncated

        content_repr = repr(self.content)
        if len(content_repr) > 100:
            content_repr = content_repr[:97] + "..."

        dict_ = self.model_dump()
        extra_fields = dict_.pop("extra_fields", {})

        repr_str = (
            f"{self.class_name()}("
            f"id={repr(self.id)}, "
            f"timestamp={str(self.created_datetime)[:-6]}, "
            f"content={content_repr}, "
            f"metadata={truncate_dict(self.metadata.content)}, "
        )

        for i, j in dict_.items():
            if i not in DEFAULT_SERIALIZATION_INCLUDE:
                if isinstance(j, dict):
                    repr_str += f"{i}={truncate_dict(j)}, "
                elif isinstance(j, str):
                    j_repr = j
                    if len(j) > 100:
                        j_repr = j[:97] + "..."
                    repr_str += f"{i}={j_repr}, "
                else:
                    repr_str += f"{i}={j}, "

        repr_str += f"extra_fields={truncate_dict(extra_fields)})"
        return repr_str

    def adapt_to(self, obj_key: str, /, *args, **kwargs: Any) -> Any:
        return self._get_adapter_registry().adapt_to(
            self, obj_key, *args, **kwargs
        )

    @classmethod
    def list_adapters(cls):
        return cls._get_adapter_registry().list_adapters()

    @classmethod
    def register_adapter(cls, adapter: type[Adapter]):
        cls._get_adapter_registry().register(adapter)

    @classmethod
    def _get_adapter_registry(cls) -> AdapterRegistry:
        """Get the converter registry for the class."""
        if isinstance(cls._adapter_registry, type):
            cls._adapter_registry = cls._adapter_registry()
        return cls._adapter_registry

    @classmethod
    def adapt_from(cls, obj: Any, obj_key: str, /, **kwargs: Any):
        dict_ = cls._get_adapter_registry().adapt_from(
            cls, obj, obj_key, **kwargs
        )
        return cls.from_dict(dict_)


# File: lion/protocols/component.py
