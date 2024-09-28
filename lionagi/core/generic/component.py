from typing import Any, ClassVar

from lion_core.converter import Converter
from lion_core.generic.component import Component as CoreComponent
from lion_core.generic.note import Note
from lionfuncs import LN_UNDEFINED, format_deprecation_msg
from pydantic import Field
from pydantic.fields import FieldInfo
from typing_extensions import Annotated, deprecated, override

from lionagi.core.generic._component_registry import ComponentConverterRegistry

NAMED_FIELD = Annotated[str, Field(..., alias="field")]


class Component(CoreComponent):
    """
    attr:
        ln_id: str
        timestamp: float
        metadata: Note
        content: Any
        embedding: list[float]
        extra_fileds: dict
    """

    _converter_registry: ClassVar = ComponentConverterRegistry

    # class methods
    @classmethod
    def from_dict(cls, data: dict, /, **kwargs):
        """
        must use from_dict, do not use __init__ to create instance
        """
        return super().from_dict(data, **kwargs)

    @classmethod
    def from_obj(cls, obj: Any, /, **kwargs):
        """
        basically obj -> dict -> from_dict
        """
        ...

    @classmethod
    def convert_from(cls, object_: Any, object_key: str = None, /, **kwargs):
        return super().convert_from(object_, object_key, **kwargs)

    @classmethod
    def register_converter(cls, converter: type[Converter]) -> None:
        """Register a new converter."""
        cls.get_converter_registry().register(converter=converter)

    # properties
    @property
    def all_fields(self):
        return super().all_fields

    # fields_methods
    def add_field(
        self,
        field_name: NAMED_FIELD,
        /,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        super().add_field(
            field_name=field_name,
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
        super().update_field(
            field_name=field_name,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            **kwargs,
        )

    # field management methods
    def field_setattr(
        self,
        field_name: str,
        attr: Any,
        value: Any,
        /,
    ) -> None:
        super().field_setattr(field_name, attr, value)

    def field_hasattr(
        self,
        field_name: str,
        attr: str,
        /,
    ) -> bool:
        return super().field_hasattr(field_name, attr)

    def field_getattr(
        self,
        field_name: str,
        attr: str,
        default: Any = LN_UNDEFINED,
        /,
    ) -> Any:
        return super().field_getattr(field_name, attr, default)

    def field_annotation(self, field_name: Any, /) -> dict[str, Any]:
        """Get the annotation of a field."""
        return super().field_annotation(field_name)

    @override
    def to_dict(self, **kwargs: Any) -> dict:
        """
        Convert the component to a dictionary representation.

        Args:
            **kwargs: Additional arguments to pass to model_dump.

        Returns:
            dict[str, Any]: A dictionary representation of the component.
        """
        return super().to_dict(**kwargs)

    def to_note(self, **kwargs: Any) -> Note:
        return Note(**self.to_dict(**kwargs))

    # legacy methods (for backward compatibility )
    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component.to_json()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.convert_to('json')",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_json(self, **kwargs: Any) -> str:
        return self.convert_to("json", **kwargs)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component.to_json_file()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.convert_to('json_file')",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_json_file(self, **kwargs: Any) -> str:
        return self.convert_to("json_file", **kwargs)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component.to_xml()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.convert_to('xml')",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_xml(self, **kwargs: Any) -> str:
        return self.convert_to("xml", **kwargs)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component.to_xml_file()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.convert_to('xml_file')",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_xml_file(self, **kwargs: Any) -> str:
        return self.convert_to("xml_file", **kwargs)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component.to_pd_series()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.convert_to('pd_series')",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_pd_series(self, **kwargs: Any) -> str:
        return self.convert_to("pd_series", **kwargs)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component.to_llama_index_node()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.convert_to('llama_index')",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_llama_index_node(self, **kwargs: Any) -> str:
        return self.convert_to("llama_index", **kwargs)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component.to_langchain_doc()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.convert_to('langchain')",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_langchain_doc(self, **kwargs: Any) -> str:
        format_deprecation_msg("to_langchain_doc", "convert_to('langchain')")
        return self.convert_to("langchain", **kwargs)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component._meta_pop()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.metadata.pop()",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _meta_pop(self, indices, default=LN_UNDEFINED):
        format_deprecation_msg("_meta_pop", "metadata.pop()")
        return self.metadata.pop(indices, default)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component._meta_insert()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.metadata.insert()",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _meta_insert(self, indices, value):
        format_deprecation_msg("_meta_insert", "metadata.insert()")
        self.metadata.insert(indices, value)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component._meta_set()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.metadata.set()",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _meta_set(self, indices, value):
        format_deprecation_msg("_meta_set", "metadata.set()")
        self.metadata.set(indices, value)

    @deprecated(
        format_deprecation_msg(
            deprecated_name="Component._meta_get()",
            type_="method",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="Component.metadata.get()",
        ),
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _meta_get(self, indices, default=LN_UNDEFINED):
        format_deprecation_msg("_meta_get", "metadata.get()")
        return self.metadata.get(indices, default)
