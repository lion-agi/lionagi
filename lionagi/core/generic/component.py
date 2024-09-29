from pathlib import Path
from typing import Any, ClassVar, Literal

import pandas as pd
from lion_core.generic.component import Component as CoreComponent
from lionfuncs import LN_UNDEFINED, read_file, to_dict
from pydantic import Field
from typing_extensions import Annotated, deprecated

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

    @classmethod
    def from_obj(
        cls,
        obj: Any,
        /,
        handle_how: Literal["suppress", "raise", "coerce", "coerce_key"] = "raise",
        **kwargs: Any,
    ):
        if isinstance(obj, pd.DataFrame):
            obj = [i for _, i in obj.iterrows()]
        if isinstance(obj, (list, tuple)) and len(obj) > 1:
            return [
                cls._dispatch_from_obj(i, handle_how=handle_how, **kwargs) for i in obj
            ]

        return cls._dispatch_from_obj(obj, handle_how=handle_how, **kwargs)

    @classmethod
    def _dispatch_from_obj(
        cls,
        obj: Any,
        /,
        handle_how: Literal["suppress", "raise", "coerce", "coerce_key"] = "raise",
        **kwargs: Any,
    ):

        try:
            obj = cls._obj_to_dict(obj, **kwargs)
            if any(
                key in obj
                for key in [
                    "lc_id_",
                    "lc_metadata",
                    "lc_type",
                    "page_content",
                ]
            ):
                return cls.convert_from(obj, "langchain", **kwargs)
            elif any(
                key in obj
                for key in [
                    "llama_index_id",
                    "llama_index_metadata",
                    "excluded_llm_metadata_keys",
                ]
            ):
                return cls.convert_from(obj, "llamaindex", **kwargs)
            else:
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
        """
        Create a Component instance from various object types.
        kwargs for to_dict and convert_from
        """

        # Unpack if obj is a single-element list or tuple
        if isinstance(obj, (list, tuple)) and len(obj) == 1:
            obj = obj[0]
        kwargs["suppress"] = True
        kwargs["fuzzy_parse"] = True
        data_, dict_ = None, None

        if isinstance(obj, pd.Series):
            return obj.to_dict()

        if isinstance(obj, Path):
            try:
                data_ = read_file(obj)
                if data_ is not None:
                    suffix = Path(obj).suffix.lower().strip(".") + "_file"
                if suffix not in cls._get_converter_registry().list_obj_keys():
                    raise ValueError(f"Unsupported file type: {Path(obj).suffix}")
            except FileNotFoundError:
                pass
            except Exception as e:
                raise ValueError(f"Unsupported file type: {obj.suffix}") from e

        if isinstance(obj, str) and "." in obj:
            suffix = obj.split(".")[-1].lower() + "_file"
            if suffix in cls._get_converter_registry().list_obj_keys():
                try:
                    data_ = read_file(obj)
                except FileNotFoundError:
                    pass
                except Exception as e:
                    raise ValueError(f"Unsupported file type: {obj.suffix}") from e

        if isinstance(data_, str):
            if "{" in obj and "}" in obj:
                dict_ = to_dict(obj, str_type="json", **kwargs)
            if dict_ is None and "<" in obj and ">" in obj:
                dict_ = to_dict(obj, str_type="xml", **kwargs)
            if dict_ is not None:
                obj = dict_
            else:
                msg = str(data_)
                msg = msg[:100] + "..." if len(msg) > 100 else msg
                raise ValueError(
                    f"The value input cannot be converted to a valid dict: {msg}"
                )

        if dict_ is None:
            kwargs["suppress"] = True
            kwargs["fuzzy_parse"] = True
            dict_ = to_dict(obj, **kwargs)
            if dict_ is None:
                raise ValueError(f"Unsupported object type: {type(obj)}")
            else:
                obj = dict_

        if isinstance(obj, dict):
            return obj

        try:
            kwargs["suppress"] = False
            return to_dict(obj, **kwargs)
        except Exception:
            pass

        # If we reach here, we don't know how to handle obj
        raise ValueError(f"Unsupported object type: {type(obj)}")

    # legacy methods (for backward compatibility )

    @property
    @deprecated(
        "Use Component.all_fields instead", category=DeprecationWarning, stacklevel=2
    )
    def _all_fields(self):
        return self.all_fields

    @property
    @deprecated(
        "Use Component.field_annotation instead",
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
        "Use Component.add_field() instead", category=DeprecationWarning, stacklevel=2
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
