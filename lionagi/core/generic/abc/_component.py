"""Component class, base building block in LionAGI"""

from abc import ABC
from functools import singledispatchmethod
from typing import Any, TypeVar, Type, TypeAlias, Union

from pandas import DataFrame, Series
from pydantic import BaseModel, Field, ValidationError, AliasChoices

from lionagi.libs import ParseUtil, SysUtil
from lionagi.libs.ln_convert import strip_lower, to_dict, to_str
from lionagi.libs.ln_func_call import lcall
from lionagi.libs.ln_nested import nget, nset, ninsert, flatten, unflatten

from ._exceptions import LionFieldError, LionTypeError, LionValueError
from ._util import base_lion_fields, llama_meta_fields, lc_meta_fields

T = TypeVar("T")


class Component(BaseModel, ABC):
    """Represents a distinguishable, temporal entity in the LionAGI system.

    Encapsulates essential attributes and behaviors needed for individual
    components within the system's architecture. Each component is uniquely
    identifiable, with built-in version control and metadata handling.

    Attributes:
        ln_id (str): A unique identifier for the component.
        timestamp (str): The UTC timestamp when the component was created.
        metadata (dict): Additional metadata for the component.
        extra_fields (dict): Additional fields for the component.
        last_updated (str): The UTC timestamp of the last update.
        content (Any): Optional content of the component.
    """

    ln_id: str = Field(
        default_factory=SysUtil.create_id,
        title="ID",
        description="A 32-char unique hash identifier.",
        frozen=True,
        validation_alias=AliasChoices("node_id", "ID", "id"),
    )

    timestamp: str = Field(
        default_factory=lambda: SysUtil.get_timestamp(sep=None)[:-6],
        title="Creation Timestamp",
        description="The UTC timestamp of creation",
        frozen=True,
        alias="created",
        validation_alias=AliasChoices("created_on", "creation_date"),
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("meta", "info"),
        description="Additional metadata for the component.",
    )

    extra_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional fields for the component.",
        validation_alias=AliasChoices(
            "extra", "additional_fields", "schema_extra", "extra_schema"
        ),
    )

    content: Any = Field(
        default=None,
        description="The optional content of the node.",
        validation_alias=AliasChoices("text", "page_content", "chunk_content", "data"),
    )

    class Config:
        """Model configuration settings."""

        extra = "allow"
        arbitrary_types_allowed = True
        populate_by_name = True
        use_enum_values = True

    @singledispatchmethod
    @classmethod
    def from_obj(cls, obj: Any, /, **kwargs) -> T:
        """Create Component instance(s) from various input types.

        This method dynamically handles different types of input data, allowing
        the creation of Component instances from dictionaries, strings (JSON),
        lists, pandas Series, pandas DataFrames, and instances of other
        classes, including Pydantic models.

        The type of the input data determines how it is processed:
        - `dict`: Treated as field-value pairs for the Component.
        - `str`: Expected to be JSON format; parsed into a dictionary first.
        - `list`: Each item is processed independently, and a list of Components
                  is returned.
        - `pandas.Series`: Converted to a dictionary; treated as field-value
                           pairs.
        - `pandas.DataFrame`: Each row is treated as a separate Component;
                              returns a list of Components.
        - `Pydantic BaseModel`: Extracts data directly from the Pydantic model.
        """
        if not isinstance(obj, (dict, str, list, Series, DataFrame, BaseModel)):
            type_ = str(type(obj))
            if "llama_index" in type_:
                dict_ = obj.to_dict()

                SysUtil.change_dict_key(dict_, "text", "content")
                metadata = dict_.pop("metadata", {})
                for i in llama_meta_fields:
                    metadata[i] = dict_.pop(i, None)

                SysUtil.change_dict_key(metadata, "class_name", "llama_index_class")
                SysUtil.change_dict_key(metadata, "id_", "llama_index_id")
                SysUtil.change_dict_key(
                    metadata, "relationships", "llama_index_relationships"
                )

                dict_["metadata"] = metadata
                return cls.from_obj(dict_)

            elif "langchain" in type_:
                dict_ = obj.to_json()
                return cls.from_obj(dict_)

        raise LionTypeError(f"Unsupported type: {type(obj)}")

    @from_obj.register(dict)
    @classmethod
    def _from_dict(cls, obj: dict, /, *args, **kwargs) -> T:
        """Create a Component instance from a dictionary."""
        try:
            dict_ = {**obj, **kwargs}

            if "lc" in dict_:
                SysUtil.change_dict_key(dict_, "page_content", "content")

                metadata = dict_.pop("metadata", {})
                metadata.update(dict_.pop("kwargs", {}))

                if not isinstance(metadata, dict):
                    metadata = {"extra_meta": metadata}

                for i in base_lion_fields:
                    if i in metadata:
                        dict_[i] = metadata.pop(i)

                for k in list(metadata.keys()):
                    if k not in lc_meta_fields:
                        dict_[k] = metadata.pop(k)

                for i in lc_meta_fields:
                    if i in dict_:
                        metadata[i] = dict_.pop(i)

                SysUtil.change_dict_key(metadata, "lc", "langchain")
                SysUtil.change_dict_key(metadata, "type", "lc_type")
                SysUtil.change_dict_key(metadata, "id", "lc_id")

                extra_fields = {
                    k: v for k, v in metadata.items() if k not in lc_meta_fields
                }
                metadata = {k: v for k, v in metadata.items() if k in lc_meta_fields}
                dict_["metadata"] = metadata
                dict_.update(extra_fields)

            else:
                meta_ = dict_.pop("metadata", None) or {}
                if not isinstance(meta_, dict):
                    meta_ = {"extra_meta": meta_}

                for k in list(dict_.keys()):
                    if k not in base_lion_fields:
                        meta_[k] = dict_.pop(k)

                if not dict_.get("content", None):
                    if "page_content" in meta_:
                        dict_["content"] = meta_.pop("page_content")
                    elif "text" in meta_:
                        dict_["content"] = meta_.pop("text")
                    elif "chunk_content" in meta_:
                        dict_["content"] = meta_.pop("chunk_content")
                    elif "data" in meta_:
                        dict_["content"] = meta_.pop("data")

                dict_["metadata"] = meta_

                if "ln_id" not in dict_:
                    if "ln_id" in meta_:
                        dict_["ln_id"] = meta_.pop("ln_id")
                    else:
                        dict_["ln_id"] = SysUtil.create_id()
                if "timestamp" not in dict_:
                    dict_["timestamp"] = SysUtil.get_timestamp(sep=None)[:-6]
                if "metadata" not in dict_:
                    dict_["metadata"] = {}
                if "extra_fields" not in dict_:
                    dict_["extra_fields"] = {}

            self = cls.model_validate(dict_, *args, **kwargs)
            return self

        except ValidationError as e:
            raise LionValueError("Invalid dictionary for deserialization.") from e

    @from_obj.register(str)
    @classmethod
    def _from_str(cls, obj: str, /, *args, fuzzy_parse: bool = False, **kwargs) -> T:
        """Create a Component instance from a JSON string."""
        obj = ParseUtil.fuzzy_parse_json(obj) if fuzzy_parse else to_dict(obj)
        try:
            return cls.from_obj(obj, *args, **kwargs)
        except ValidationError as e:
            raise LionValueError("Invalid JSON for deserialization: ") from e

    @from_obj.register(list)
    @classmethod
    def _from_list(cls, obj: list, /, *args, **kwargs) -> list[T]:
        """Create a list of node instances from a list of objects."""
        return [cls.from_obj(item, *args, **kwargs) for item in obj]

    @from_obj.register(Series)
    @classmethod
    def _from_pd_series(
        cls, obj: Series, /, *args, pd_kwargs: dict | None = None, **kwargs
    ) -> T:
        """Create a node instance from a Pandas Series."""
        pd_kwargs = pd_kwargs or {}
        return cls.from_obj(obj.to_dict(**pd_kwargs), *args, **kwargs)

    @from_obj.register(DataFrame)
    @classmethod
    def _from_pd_dataframe(
        cls,
        obj: DataFrame,
        /,
        *args,
        pd_kwargs: dict | None = None,
        include_index=False,
        **kwargs,
    ) -> list[T]:
        """Create a list of node instances from a Pandas DataFrame."""
        pd_kwargs = pd_kwargs or {}

        _objs = []
        for index, row in obj.iterrows():
            _obj = cls.from_obj(row, *args, **pd_kwargs, **kwargs)
            if include_index:
                _obj.metadata["df_index"] = index
            _objs.append(_obj)

        return _objs

    @from_obj.register(BaseModel)
    @classmethod
    def _from_base_model(cls, obj, /, pydantic_kwargs=None, **kwargs) -> T:
        """Create a node instance from a Pydantic BaseModel."""
        pydantic_kwargs = pydantic_kwargs or {"by_alias": True}
        try:
            config_ = obj.model_dump(**pydantic_kwargs)
        except:
            try:
                if hasattr(obj, "to_dict"):
                    config_ = obj.to_dict(**pydantic_kwargs)
                elif hasattr(obj, "dict"):
                    config_ = obj.dict(**pydantic_kwargs)
                else:
                    raise LionValueError(
                        "Invalid Pydantic model for deserialization: "
                        "missing 'to_dict'(V2) or 'dict'(V1) method."
                    )
            except Exception as e:
                raise LionValueError(
                    f"Invalid Pydantic model for deserialization: {e}"
                ) from e
        return cls.from_obj(config_ | kwargs)

    @classmethod
    def class_name(cls) -> str:
        """Get the class name."""
        return cls.__name__

    def to_json_str(self, *args, **kwargs) -> str:
        """Convert the component to a JSON string."""
        dict_ = self.to_dict(*args, **kwargs)
        return to_str(dict_)

    def to_dict(self, *args, **kwargs) -> dict[str, Any]:
        """Convert the component to a dictionary."""
        dict_ = self.model_dump(*args, by_alias=True, **kwargs)
        for field_name in list(self.extra_fields.keys()):
            if field_name not in dict_:
                dict_[field_name] = getattr(self, field_name, None)
        dict_.pop("extra_fields", None)
        return dict_

    def to_xml(self, *args, **kwargs) -> str:
        """Convert the component to an XML string."""
        import xml.etree.ElementTree as ET

        root = ET.Element(self.__class__.__name__)

        def convert(dict_obj: dict, parent: ET.Element) -> None:
            for key, val in dict_obj.items():
                if isinstance(val, dict):
                    element = ET.SubElement(parent, key)
                    convert(val, element)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(val)

        convert(self.to_dict(*args, **kwargs), root)
        return ET.tostring(root, encoding="unicode")

    def to_pd_series(self, *args, pd_kwargs=None, **kwargs) -> Series:
        """Convert the node to a Pandas Series."""
        pd_kwargs = pd_kwargs or {}
        dict_ = self.to_dict(*args, **kwargs)
        return Series(dict_, **pd_kwargs)

    def to_llama_index(self, node_type: Type | str | Any = None, **kwargs) -> Any:
        """Serializes this node for LlamaIndex."""
        from lionagi.integrations.bridge import LlamaIndexBridge

        return LlamaIndexBridge.to_llama_index_node(self, node_type=node_type, **kwargs)

    def to_langchain(self, **kwargs) -> Any:
        """Serializes this node for Langchain."""
        from lionagi.integrations.bridge import LangchainBridge

        return LangchainBridge.to_langchain_document(self, **kwargs)

    def _update_count(self, name):
        if (a := nget(self.metadata, ["last_updated", name], None)) is None:
            ninsert(
                self.metadata,
                ["last_updated", name],
                (1, SysUtil.get_timestamp(sep=None)[:-6]),
            )
        elif isinstance(a, tuple) and isinstance(a[0], int):
            nset(
                self.metadata,
                ["last_updated", name],
                (a[0] + 1, SysUtil.get_timestamp(sep=None)[:-6]),
            )

    def _meta_pop(self, indices, default=...):
        indices = (
            indices
            if not isinstance(indices, list)
            else "[^_^]".join([i if isinstance(i, str) else str(i) for i in indices])
        )
        dict_ = self.metadata.copy()
        dict_ = flatten(dict_)
        try:
            out_ = dict_.pop(indices, default) if default != ... else dict_.pop(indices)
        except KeyError as e:
            if default == ...:
                raise KeyError(f"Key {indices} not found in metadata.") from e
            return default
        a = unflatten(dict_)
        self.metadata.clear()
        self.metadata.update(a)
        return out_

    def _meta_insert(self, indices, value):
        ninsert(self.metadata, indices, value)

    def _meta_set(self, indices, value):
        if not self._meta_get(indices):
            self._meta_insert(indices, value)
        nset(self.metadata, indices, value)

    def _meta_get(self, indices):
        return nget(self.metadata, indices, None)

    def __setattr__(self, name, value):
        if name == "metadata":
            return
        super().__setattr__(name, value)
        self._update_count(name)

    def _add_field(
        self,
        field: str,
        annotation: Any = None,
        default: Any = None,
        value: Any = None,
        field_obj: Any = None,
        **kwargs,
    ) -> None:
        """Add a field to the model after initialization."""
        self.extra_fields[field] = field_obj or Field(default=default, **kwargs)
        if annotation:
            self.extra_fields[field].annotation = annotation

        if not value and (a := self._get_field_attr(field, "default", None)):
            value = a

        self.__setattr__(field, value)

    @property
    def _all_fields(self):
        return {**self.model_fields, **self.extra_fields}

    @property
    def _field_annotations(self) -> dict:
        """Return the annotations for each field in the model."""
        return self._get_field_annotation(list(self._all_fields.keys()))

    def _get_field_attr(self, k: str, attr: str, default: Any = False) -> Any:
        """Get the value of a field attribute."""
        try:
            if not self._field_has_attr(k, attr):
                raise LionFieldError(f"field {k} has no attribute {attr}")

            field = self._all_fields[k]
            if not (a := getattr(field, attr, None)):
                try:
                    return field.json_schema_extra[attr]
                except Exception:
                    return None
            return a
        except Exception as e:
            if default is not False:
                return default
            raise e

    @singledispatchmethod
    def _get_field_annotation(self, field_name: Any) -> Any:
        raise LionTypeError

    @_get_field_annotation.register(str)
    def _(self, field_name: str) -> dict[str, Any]:
        dict_ = {field_name: self._all_fields[field_name].annotation}
        for k, v in dict_.items():
            if "|" in str(v):
                v = str(v)
                v = v.split("|")
                dict_[k] = lcall(v, strip_lower)
            else:
                dict_[k] = [v.__name__]
        return dict_

    @_get_field_annotation.register(list)
    @_get_field_annotation.register(tuple)
    def _(self, field_names: list | tuple) -> dict[str, Any]:
        dict_ = {}
        for field_name in field_names:
            dict_.update(self._get_field_annotation(field_name))
        return dict_

    def _field_has_attr(self, k: str, attr: str) -> bool:
        """Check if a field has a specific attribute."""

        if not (field := self._all_fields.get(k, None)):
            raise KeyError(f"Field {k} not found in model fields.")

        if not attr in str(field):
            try:
                a = (
                    attr in self._all_fields[k].json_schema_extra
                    and self._all_fields[k].json_schema_extra[attr] is not None
                )
                return a if isinstance(a, bool) else False
            except Exception:
                return False
        return True

    def __str__(self):
        dict_ = self.to_dict()
        dict_["class_name"] = self.class_name()
        return Series(dict_).__str__()

    def __repr__(self):
        dict_ = self.to_dict()
        dict_["class_name"] = self.class_name()
        return Series(dict_).__repr__()

    def __len__(self):
        return 1


LionIDable: TypeAlias = Union[str, Component]


def get_lion_id(item: LionIDable) -> str:
    """Get the Lion ID of an item."""
    if not isinstance(item, (str, Component)):
        raise LionTypeError("Item must be a single LionIDable object.")
    return item.ln_id if isinstance(item, Component) else item
