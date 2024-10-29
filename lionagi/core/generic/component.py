from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd
from lion_core.generic.component import Component
from lionfuncs import LN_UNDEFINED, to_dict, to_json, to_str
from typing_extensions import deprecated

from ._component_adapters import ComponentAdapterRegistry


def from_obj(
    cls,
    obj: Any,
    /,
    handle_how: Literal["suppress", "raise", "coerce", "coerce_key"] = "raise",
    fuzzy_parse: bool = False,
) -> Component | list[Component]:

    if isinstance(obj, pd.DataFrame):
        obj = [i for _, i in obj.iterrows()]

    def _obj_to_dict(obj_: Any, /) -> dict:

        dict_ = None

        if isinstance(obj_, dict):
            return obj_

        fp = None
        if isinstance(obj_, str):
            try:
                fp = Path(obj_)
            except Exception:
                pass
        fp = fp or obj_
        if isinstance(fp, Path):
            suffix = fp.suffix
            if suffix in cls.list_adapters():
                return cls.adapt_from(obj_, suffix)

        if isinstance(obj_, str):
            if "{" in obj_ or "}" in obj_:
                dict_ = to_json(obj_, fuzzy_parse=fuzzy_parse)
            if isinstance(dict_, dict):
                return dict_
            else:
                msg = obj_[:100] + "..." if len(obj_) > 100 else obj_
                raise ValueError(
                    f"The value input cannot be converted to a valid dict: {msg}"
                )

        dict_ = to_dict(obj_, suppress=True)
        if not dict_:
            raise ValueError(f"Unsupported object type: {type(obj)}")
        return dict_

    def _dispatch_from_obj(
        obj_: Any,
        /,
        handle_how: Literal[
            "suppress", "raise", "coerce", "coerce_key"
        ] = "raise",
    ) -> Component:
        try:
            type_ = (
                str(type(obj_))
                .strip("_")
                .strip("<")
                .strip(">")
                .strip(".")
                .lower()
            )

            if "langchain" in type_:
                return cls.adapt_from(obj_, "langchain_doc")

            if "llamaindex" in type_:
                return cls.adapt_from(obj_, "llama_index_node")

            if "pandas" in type_ and "series" in type_:
                return cls.adapt_from(obj_, "pd_series")

            obj_ = _obj_to_dict(obj_)
            return cls.from_dict(obj_)

        except Exception as e:
            if handle_how == "raise":
                raise e
            if handle_how == "coerce":
                return cls.from_dict({"content": obj_})
            if handle_how == "suppress":
                return None
            if handle_how == "coerce_key":
                return cls.from_dict({str(k): v for k, v in obj_.items()})

    if isinstance(obj, (list, tuple)) and len(obj) > 1:
        return [_dispatch_from_obj(i, handle_how=handle_how) for i in obj]
    return _dispatch_from_obj(obj, handle_how=handle_how)


# legacy methods (for backward compatibility )


@deprecated(
    "Use Component.all_fields instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _all_fields(self):
    return self.all_fields


@deprecated(
    "Use BaseModel.__annotations__ instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def _field_annotations(self, *args, **kwargs) -> dict[str, Any]:
    return self.__annotations__


@deprecated(
    "Use Component.adapt_to('json') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_json_str(self, *args, **kwargs) -> str:
    return self.adapt_to("json")


@deprecated(
    "Use Component.convert_to('.json') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_json_file(self, *args, **kwargs) -> str:
    return self.adapt_to(".json", **kwargs)


@deprecated(
    "Use Component.adapt_to('pd_series') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_pd_series(self, *args, **kwargs) -> str:
    return self.adapt_to("pd_series", **kwargs)


@deprecated(
    "Use Component.adapt_to('llama_index_node') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_llama_index_node(self, *args, **kwargs) -> str:
    return self.adapt_to("llama_index_node", **kwargs)


@deprecated(
    "Use Component.adapt_to('langchain_doc') instead",
    category=DeprecationWarning,
    stacklevel=2,
)
def to_langchain_doc(self, *args, **kwargs) -> str:
    return self.adapt_to("langchain_doc", **kwargs)


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


deprecated_methods = {
    "_all_fields": _all_fields,
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
