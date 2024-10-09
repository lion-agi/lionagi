code1 = '''
from collections import deque
from functools import singledispatchmethod
from typing import Annotated, Any, ClassVar, TypeVar

from lionabc.exceptions import LionValueError
from lionfuncs import LN_UNDEFINED, copy, time
from pydantic import Field, field_serializer, field_validator
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from typing_extensions import override

from lion_core._class_registry import get_class
from lion_core.converter import Converter
from lion_core.generic.component_converter import ComponentConverterRegistry
from lion_core.generic.element import Element
from lion_core.generic.note import Note

T = TypeVar("T", bound=Element)

DEFAULT_SERIALIZATION_INCLUDE: set[str] = {
    "ln_id",
    "timestamp",
    "metadata",
    "content",
    "embedding",
}


NAMED_FIELD = Annotated[str, Field(..., alias="field")]


class Component(Element):
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

    extra_fields: dict[str, Any] = Field(default_factory=dict)

    _converter_registry: ClassVar = ComponentConverterRegistry

    @field_serializer("metadata")
    def _serialize_metadata(self, value):
        return value.to_dict()

    @field_serializer("extra_fields")
    def _serialize_extra_fields(
        self,
        value: dict[str, FieldInfo],
    ) -> dict[str, Any]:
        """Custom serializer for extra fields."""
        output_dict = {}
        for k in value.keys():
            k_value = self.__dict__.get(k)
            output_dict[k] = k_value
        return output_dict

    @field_validator("extra_fields")
    def _validate_extra_fields(cls, value: Any) -> dict[str, FieldInfo]:
        """Custom validator for extra fields."""
        if not isinstance(value, dict):
            raise LionValueError("Extra fields must be a dictionary")

        out_ = {}
        for k, v in value.items():
            out_[k] = Field(**v) if isinstance(v, dict) else v

        return out_

    @property
    def all_fields(self) -> dict[str, FieldInfo]:
        """
        Get all fields including model fields and extra fields.

        Returns:
            dict[str, FieldInfo]: A dictionary containing all fields.
        """
        return {**self.model_fields, **self.extra_fields}

    def add_field(
        self,
        field_name: NAMED_FIELD,
        /,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo = LN_UNDEFINED,
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
            raise LionValueError(f"Field '{field_name}' already exists")

        self.update_field(
            field_name,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            **kwargs,
        )

    # when updating field, we do not check the validity of annotation
    # meaning current value will not get validated, and can lead to
    # errors when storing and loading if you change annotation to a type
    # that is not compatible with the current value
    def update_field(
        self,
        field_name: NAMED_FIELD,
        /,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
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

        # handle field_obj
        if field_obj is not LN_UNDEFINED:
            if not isinstance(field_obj, FieldInfo):
                raise ValueError(
                    "Invalid field_obj, should be a pydantic FieldInfo object"
                )
            self.extra_fields[field_name] = field_obj

        # handle kwargs
        if kwargs:
            if field_name in self.all_fields:  # existing field
                for k, v in kwargs.items():
                    self.field_setattr(field_name, k, v)
            else:
                self.extra_fields[field_name] = Field(**kwargs)

        # handle no explicit defined field
        if field_obj is LN_UNDEFINED and not kwargs:
            if field_name not in self.all_fields:
                self.extra_fields[field_name] = Field()

        field_obj = self.all_fields[field_name]

        # handle annotation
        if annotation is not LN_UNDEFINED:
            field_obj.annotation = annotation
        if not field_obj.annotation:
            field_obj.annotation = Any

        # handle value
        if value is LN_UNDEFINED:
            if getattr(self, field_name, LN_UNDEFINED) is not LN_UNDEFINED:
                value = getattr(self, field_name)

            elif getattr(field_obj, "default") is not PydanticUndefined:
                value = field_obj.default

            elif getattr(field_obj, "default_factory"):
                value = field_obj.default_factory()

        setattr(self, field_name, value)
        self._add_last_update(field_name)

    def _add_last_update(self, field_name: str, /) -> None:
        current_time = time()
        self.metadata.set(["last_updated", field_name], current_time)

    @override
    def to_dict(self, **kwargs: Any) -> dict:
        """
        Convert the component to a dictionary representation.

        Args:
            **kwargs: Additional arguments to pass to model_dump.

        Returns:
            dict[str, Any]: A dictionary representation of the component.
        """
        dict_ = self.model_dump(**kwargs)
        if isinstance(self.content, Note):
            dict_["content"] = dict_["content"]["content"]
        extra_fields = dict_.pop("extra_fields", {})
        dict_ = {**dict_, **extra_fields, "lion_class": self.class_name()}
        for i in list(dict_.keys()):
            if dict_[i] is LN_UNDEFINED:
                dict_.pop(i)
        return dict_

    def to_note(self, **kwargs: Any) -> Note:
        return Note(**self.to_dict(**kwargs))

    @override
    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> T:
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
            return LN_UNDEFINED

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
            f"ln_id={self.ln_id[:8]}..., "
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
            f"ln_id={repr(self.ln_id)}, "
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

    # converter methods
    @classmethod
    def list_converters(cls) -> list[str]:
        """List all registered converters."""
        return cls._get_converter_registry().list_obj_keys()

    @classmethod
    def _get_converter_registry(cls) -> ComponentConverterRegistry:
        """Get the converter registry for the class."""
        if isinstance(cls._converter_registry, type):
            cls._converter_registry = cls._converter_registry()
        return cls._converter_registry

    def convert_to(self, obj_key: str, /, **kwargs: Any) -> Any:
        """Convert the component to a specified type"""
        return self._get_converter_registry().convert_to(
            self,
            obj_key,
            **kwargs,
        )

    @classmethod
    def convert_from(
        cls, obj: Any, obj_key: str = None, /, **kwargs: Any
    ) -> T:
        """Convert data to create a new component instance"""
        data = cls._get_converter_registry().convert_from(
            cls,
            obj,
            obj_key,
            **kwargs,
        )
        return cls.from_dict(data)

    @classmethod
    def register_converter(cls, converter: type[Converter]) -> None:
        """Register a new converter."""
        cls._get_converter_registry().register(converter)

    # field management methods
    def field_setattr(
        self,
        field_name: str,
        attr: Any,
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
        default: Any = LN_UNDEFINED,
        /,
    ) -> Any:
        """Get the value of a field attribute."""
        if str(attr).strip("s").lower() == "annotation":
            return self._field_annotation(field_name)

        all_fields = self.all_fields
        if field_name not in all_fields:
            raise KeyError(f"Field {field_name} not found in object fields.")
        field_obj = all_fields[field_name]

        # check fieldinfo attr

        value = getattr(field_obj, attr, LN_UNDEFINED)
        if value is not LN_UNDEFINED:
            return value
        else:
            if isinstance(field_obj.json_schema_extra, dict):
                value = field_obj.json_schema_extra.get(attr, LN_UNDEFINED)
                if value is not LN_UNDEFINED:
                    return value

        # undefined attr
        if default is not LN_UNDEFINED:
            return default
        else:
            raise AttributeError(
                f"field {field_name} has no attribute {attr}",
            )

    def field_annotation(self, field_name: Any, /) -> dict[str, Any]:
        """Get the annotation of a field."""
        return self._field_annotation(field_name)

    @singledispatchmethod
    def _field_annotation(self, field_name: Any, /) -> dict[str, Any]:
        """
        Get field annotation for a given field.

        Args:
            field: The field to get annotation for.

        Returns:
            A dictionary containing the field annotation.
        """
        return {}

    @_field_annotation.register(str)
    def _(self, field_name: str, /) -> dict[str, Any]:
        dict_ = {field_name: self.all_fields[field_name].annotation}
        for _f, _anno in dict_.items():
            if "|" in str(_anno):
                _anno = str(_anno)
                _anno = _anno.split("|")
                dict_[_f] = [str(i).lower().strip() for i in _anno]
            else:
                dict_[_f] = [_anno.__name__] if _anno else None
        return dict_

    @_field_annotation.register(deque)
    @_field_annotation.register(set)
    @_field_annotation.register(list)
    @_field_annotation.register(tuple)
    def _(self, field_name, /) -> dict[str, Any]:
        dict_ = {}
        for f in field_name:
            dict_.update(self._field_annotation(f))
        return dict_


__all__ = ["Component"]

# File: lion_core/generic/component.py
'''
