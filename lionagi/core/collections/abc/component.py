from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal, TypeAlias, TypeVar, Union

import pandas as pd
from lion_core.generic.component import Component as CoreComponent
from lion_core.generic.element import Element
from lionabc import Observable
from lionabc.exceptions import LionTypeError, LionValueError
from lionfuncs import LN_UNDEFINED, to_dict
from pydantic import Field
from typing_extensions import deprecated

from lionagi.core.collections.registry import ComponentAdapterRegistry
from lionagi.libs import SysUtil

NAMED_FIELD = Annotated[str, Field(..., alias="field")]

T = TypeVar("T")


class Component(CoreComponent):

    _adapter_registry: ClassVar = ComponentAdapterRegistry

    @staticmethod
    def _validate_embedding(value: Any) -> list:
        if not value:
            return []
        if isinstance(value, str):
            if len(value) < 10:
                return []

            string_elements = value.strip("[]").split(",")
            # Convert each string element to a float
            with contextlib.suppress(ValueError):
                return [float(element) for element in string_elements]
        raise ValueError("Invalid embedding format.")

    @classmethod
    def from_obj(
        cls,
        obj: Any,
        /,
        handle_how: Literal[
            "suppress", "raise", "coerce", "coerce_key"
        ] = "raise",
        **kwargs: Any,
    ) -> Component | list[Component]:
        if isinstance(obj, pd.DataFrame):
            obj = obj.to_dict(orient="records")
        if isinstance(obj, (list, tuple)):
            if len(obj) > 1:
                return [
                    cls._dispatch_from_obj(i, handle_how=handle_how, **kwargs)
                    for i in obj
                ]
            else:
                obj = obj[0]

        return cls._dispatch_from_obj(obj, handle_how=handle_how, **kwargs)

    @classmethod
    def _dispatch_from_obj(
        cls,
        obj: Any,
        /,
        handle_how: Literal[
            "suppress", "raise", "coerce", "coerce_key"
        ] = "raise",
        **kwargs: Any,
    ) -> Component:
        try:
            type_ = str(type(obj))

            if "langchain" in type_:
                return cls.adapt_from(obj, "langchain", **kwargs)

            if "llamaindex" in type_:
                return cls.adapt_from(obj, "llamaindex", **kwargs)

            obj = cls._obj_to_dict(obj, **kwargs)
            return cls.from_dict(obj)

        except Exception as e:
            if handle_how == "raise":
                raise e
            if handle_how == "coerce":
                return cls.from_dict({"content": obj})
            if handle_how == "suppress":
                return None
            if handle_how == "coerce_key":
                return cls.from_dict({str(k): v for k, v in obj.items()})

    @classmethod
    def _obj_to_dict(cls, obj: Any, /, **kwargs) -> dict:
        dict_ = None

        if isinstance(obj, dict):
            return obj

        if isinstance(obj, pd.Series):
            return obj.to_dict()

        if isinstance(obj, Path):
            suffix = Path(obj).suffix.lower().strip(".").strip() + "_file"
            if suffix in cls._get_adapter_registry().list_adapters():
                return cls._get_adapter_registry().adapt_from(
                    cls, obj, suffix, **kwargs
                )
            raise LionValueError(f"Unsupported file type: {obj.suffix}")

        if isinstance(obj, str) and "." in obj:
            suffix = obj.split(".")[-1].lower().strip() + "_file"
            if suffix in cls._get_adapter_registry().list_adapters():
                return cls._get_adapter_registry().adapt_from(
                    cls, obj, suffix, **kwargs
                )

        if isinstance(obj, str):
            kwargs["suppress"] = True
            if "{" in obj:
                dict_ = cls._get_adapter_registry().adapt_from(
                    cls, obj, "json_data", **kwargs
                )
            if not dict_ and "<" in obj and ">" in obj:
                dict_ = cls._get_adapter_registry().adapt_from(
                    cls, obj, "xml_data", **kwargs
                )
            if isinstance(dict_, dict):
                return dict_
            else:
                msg = obj[:100] + "..." if len(obj) > 100 else obj
                raise LionValueError(
                    f"The value input cannot be converted to a valid dict: {msg}"
                )

        kwargs["suppress"] = True
        dict_ = to_dict(obj, **kwargs)
        if not dict_:
            raise LionTypeError(f"Unsupported object type: {type(obj)}")
        return dict_

    # legacy methods (for backward compatibility )

    @property
    @deprecated(
        "Use Component.all_fields instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _all_fields(self):
        return self.all_fields

    @property
    @deprecated(
        "Use Component.__annotations__ instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _field_annotations(self) -> dict[str, Any]:
        return self.field_annotation(list(self.all_fields.keys()))

    @deprecated(
        "Use Component.convert_to('json') instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_json_str(self, **kwargs: Any) -> str:
        return self.convert_to("json", **kwargs)

    @deprecated(
        "Use Component.convert_to('json_file') instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_json_file(self, **kwargs: Any) -> str:
        return self.convert_to("json_file", **kwargs)

    @deprecated(
        "Use Component.convert_to('xml') instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_xml(self, **kwargs: Any) -> str:
        return self.convert_to("xml", **kwargs)

    @deprecated(
        "Use Component.convert_to('xml_file') instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_xml_file(self, **kwargs: Any) -> str:
        return self.convert_to("xml_file", **kwargs)

    @deprecated(
        "Use Component.convert_to('pd_series') instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_pd_series(self, **kwargs: Any) -> str:
        return self.convert_to("pd_series", **kwargs)

    @deprecated(
        "Use Component.convert_to('llamaindex') instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_llama_index_node(self, **kwargs: Any) -> str:
        return self.convert_to("llamaindex", **kwargs)

    @deprecated(
        "Use Component.convert_to('langchain') instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def to_langchain_doc(self, **kwargs: Any) -> str:
        return self.convert_to("langchain", **kwargs)

    @deprecated(
        "Use Component.metadata.pop() instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _meta_pop(self, indices, default=LN_UNDEFINED):
        return self.metadata.pop(indices, default)

    @deprecated(
        "Use Component.metadata.insert() instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _meta_insert(self, indices, value):
        self.metadata.insert(indices, value)

    @deprecated(
        "Use Component.metadata.set() instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _meta_set(self, indices, value):
        self.metadata.set(indices, value)

    @deprecated(
        "Use Component.metadata.get() instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _meta_get(self, indices, default=LN_UNDEFINED):
        return self.metadata.get(indices, default)

    @deprecated(
        "Use Component.field_hasattr() instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _field_has_attr(self, k, attr) -> bool:
        return self.field_hasattr(k, attr)

    @deprecated(
        "Use Component.field_getattr() instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _get_field_attr(self, k, attr, default=LN_UNDEFINED):
        return self.field_getattr(k, attr, default)

    @deprecated(
        "Use Component.add_field() instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def _add_field(
        self,
        field: str,
        annotation: Any = LN_UNDEFINED,
        default: Any = LN_UNDEFINED,
        value: Any = LN_UNDEFINED,
        field_obj: Any = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        kwargs["default"] = default
        self.add_field(
            field,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            **kwargs,
        )


LionIDable: TypeAlias = Union[str, Observable]


def get_lion_id(item: LionIDable) -> str:
    """Get the Lion ID of an item."""
    return SysUtil.get_id(item)


__all__ = ["Component", "Element", "get_lion_id", "LionIDable"]
