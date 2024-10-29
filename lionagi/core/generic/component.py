from __future__ import annotations

from typing import Any, TypeVar

from lion_core.generic.component import Component
from lionfuncs import LN_UNDEFINED
from typing_extensions import deprecated

from ._component_adapters import ComponentAdapterRegistry
from .utils import from_obj

T = TypeVar("T", bound=Component)


# legacy methods (for backward compatibility )
@deprecated(
    "Use Component.all_fields instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _all_fields(self: T):
    return self.all_fields


@deprecated(
    "Use BaseModel.__annotations__ instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _field_annotations(self: T, *args, **kwargs) -> dict[str, Any]:
    return self.__annotations__


@deprecated(
    "Use Component.adapt_to('json') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_json_str(self: T, *args, **kwargs) -> str:
    return self.adapt_to("json")


@deprecated(
    "Use Component.convert_to('.json') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_json_file(self: T, *args, **kwargs) -> str:
    return self.adapt_to(".json", **kwargs)


@deprecated(
    "Use Component.adapt_to('pd_series') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_pd_series(self: T, *args, **kwargs) -> str:
    return self.adapt_to("pd_series")


@deprecated(
    "Use Component.adapt_to('llama_index_node') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_llama_index_node(self: T, *args, **kwargs) -> str:
    return self.adapt_to("llama_index_node")


@deprecated(
    "Use Component.adapt_to('langchain_doc') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_langchain_doc(self: T, *args, **kwargs) -> str:
    return self.adapt_to("langchain_doc")


@deprecated(
    "Use Component.metadata.pop() instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _meta_pop(self: T, indices, default=LN_UNDEFINED):
    return self.metadata.pop(indices, default)


@deprecated(
    "Use Component.metadata.insert() instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _meta_insert(self: T, indices, value):
    self.metadata.insert(indices, value)


@deprecated(
    "Use Component.metadata.set() instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _meta_set(self: T, indices, value):
    self.metadata.set(indices, value)


@deprecated(
    "Use Component.metadata.get() instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _meta_get(self: T, indices, default=LN_UNDEFINED):
    return self.metadata.get(indices, default)


@deprecated(
    "Use Component.field_hasattr() instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _field_has_attr(self: T, k, attr) -> bool:
    return self.field_hasattr(k, attr)


@deprecated(
    "Use Component.field_getattr() instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _get_field_attr(self: T, k, attr, default=LN_UNDEFINED):
    return self.field_getattr(k, attr, default)


@deprecated(
    "Use Component.add_field() instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _add_field(
    self: T,
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


deprecated_methods = {
    "_all_fields": property(_all_fields),
    "_field_annotations": _field_annotations,
    "to_json_str": to_json_str,
    "to_json_file": to_json_file,
    "to_pd_series": to_pd_series,
    "to_llama_index_node": to_llama_index_node,
    "to_langchain_doc": to_langchain_doc,
    "_meta_pop": _meta_pop,
    "_meta_insert": _meta_insert,
    "_meta_set": _meta_set,
    "_meta_get": _meta_get,
    "_field_has_attr": _field_has_attr,
    "_get_field_attr": _get_field_attr,
    "_add_field": _add_field,
}


for k, v in deprecated_methods.items():
    setattr(Component, k, v)

setattr(Component, "from_obj", classmethod(from_obj))


# for method_name, method in deprecated_methods.items():
#     setattr(Component, method_name, method)

# setattr(Component, "from_obj", from_obj)

Component._adapter_registry = ComponentAdapterRegistry

__all__ = ["Component"]
