"""Component class, base building block in LionAGI."""

import contextlib
from functools import singledispatchmethod
from typing import Any, TypeAlias, TypeVar, Union

import lionfuncs as ln
from lionabc import Observable
from pandas import DataFrame, Series
from pydantic import AliasChoices, BaseModel, Field, ValidationError

from lionagi.libs import ParseUtil, SysUtil
from lionagi.libs.ln_convert import strip_lower, to_dict, to_str
from lionagi.libs.ln_func_call import lcall
from lionagi.libs.ln_nested import flatten, nget, ninsert, nset, unflatten

from .exceptions import FieldError, LionTypeError, LionValueError
from .util import base_lion_fields, lc_meta_fields, llama_meta_fields

T = TypeVar("T")

_init_class = {}


def change_dict_key(dict_: dict, old_key: str, new_key: str) -> None:
    """Change a key in a dictionary."""
    if old_key in dict_:
        dict_[new_key] = dict_.pop(old_key)


class Element(BaseModel, Observable):
    """Base class for elements within the LionAGI system.

    Attributes:
        ln_id (str): A 32-char unique hash identifier.
        timestamp (str): The UTC timestamp of creation.
    """

    ln_id: str = Field(
        default_factory=SysUtil.id,
        title="ID",
        frozen=True,
        validation_alias=AliasChoices("node_id", "ID", "id"),
    )

    timestamp: str = Field(
        default_factory=lambda: ln.time(type_="iso"),
        title="Creation Timestamp",
        description="The UTC timestamp of creation",
        frozen=True,
        alias="created",
        validation_alias=AliasChoices("created_on", "creation_date"),
    )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in _init_class:
            _init_class[cls.__name__] = cls

    # element is always true
    def __bool__(self):
        return True


class Component(Element):
    """
    Represents a distinguishable, temporal entity in LionAGI.

    Encapsulates essential attributes and behaviors needed for individual
    components within the system's architecture. Each component is uniquely
    identifiable, with built-in version control and metadata handling.

    Attributes:
        ln_id (str): A unique identifier for the component.
        timestamp (str): The UTC timestamp when the component was created.
        metadata (dict): Additional metadata for the component.
        extra_fields (dict): Additional fields for the component.
        content (Any): Optional content of the component.
    """

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
        validation_alias=AliasChoices(
            "text", "page_content", "chunk_content", "data"
        ),
    )

    embedding: list[float] = Field(
        default=[],
        description="The optional embedding of the node.",
    )

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

    class Config:
        """Model configuration settings."""

        extra = "allow"
        arbitrary_types_allowed = True
        populate_by_name = True
        use_enum_values = True

    @singledispatchmethod
    @classmethod
    def from_obj(cls, obj: Any, /, **kwargs) -> T:
        """
        Create Component instance(s) from various input types.

        This method dynamically handles different types of input data,
        allowing the creation of Component instances from dictionaries,
        strings (JSON), lists, pandas Series, pandas DataFrames, and
        instances of other classes, including Pydantic models. Additionally,
        it includes support for custom types such as LlamaIndex and
        Langchain specific data.

        The type of the input data determines how it is processed:
        - `dict`: Treated as field-value pairs for the Component.
        - `str`: Expected to be JSON format; parsed into a dictionary first.
        - `list`: Each item is processed independently, and a list of
                  Components is returned.
        - `pandas.Series`: Converted to a dictionary; treated as field-value
                           pairs.
        - `pandas.DataFrame`: Each row is treated as a separate Component;
                              returns a list of Components.
        - `Pydantic BaseModel`: Extracts data directly from the Pydantic
                                model.
        - `LlamaIndex model`: Converts using LlamaIndex-specific logic to
                              extract data suitable for Component creation.
        - `Langchain model`: Processes Langchain-specific structures to
                             produce Component data.

        Args:
            obj: The input object to create Component instance(s) from.
            **kwargs: Additional keyword arguments to pass to the creation
                      method.

        Returns:
            T: The created Component instance(s).

        Raises:
            LionTypeError: If the input type is not supported.
        """
        if isinstance(obj, (dict, str, list, Series, DataFrame, BaseModel)):
            return cls._dispatch_from_obj(obj, **kwargs)

        type_ = str(type(obj))

        if "llama_index" in type_:
            return cls._from_llama_index(obj)
        elif "langchain" in type_:
            return cls._from_langchain(obj)

        raise LionTypeError(f"Unsupported type: {type(obj)}")

    @classmethod
    def _dispatch_from_obj(cls, obj: Any, **kwargs) -> T:
        """Dispatch the from_obj method based on the input type."""
        if isinstance(obj, dict):
            return cls._from_dict(obj, **kwargs)
        elif isinstance(obj, str):
            return cls._from_str(obj, **kwargs)
        elif isinstance(obj, list):
            return cls._from_list(obj, **kwargs)
        elif isinstance(obj, Series):
            return cls._from_pd_series(obj, **kwargs)
        elif isinstance(obj, DataFrame):
            return cls._from_pd_dataframe(obj, **kwargs)
        elif isinstance(obj, BaseModel):
            return cls._from_base_model(obj, **kwargs)

    @classmethod
    def _from_llama_index(cls, obj: Any) -> T:
        """Create a Component instance from a LlamaIndex object."""
        dict_ = obj.to_dict()

        change_dict_key(dict_, "text", "content")
        metadata = dict_.pop("metadata", {})

        for field in llama_meta_fields:
            metadata[field] = dict_.pop(field, None)

        change_dict_key(metadata, "class_name", "llama_index_class")
        change_dict_key(metadata, "id_", "llama_index_id")
        change_dict_key(metadata, "relationships", "llama_index_relationships")

        dict_["metadata"] = metadata
        return cls.from_obj(dict_)

    @classmethod
    def _from_langchain(cls, obj: Any) -> T:
        """Create a Component instance from a Langchain object."""
        dict_ = obj.to_json()
        return cls.from_obj(dict_)

    @classmethod
    def _from_dict(cls, obj: dict, /, *args, **kwargs) -> T:
        """Create a Component instance from a dictionary."""
        try:
            dict_ = {**obj, **kwargs}
            if "embedding" in dict_:
                dict_["embedding"] = cls._validate_embedding(
                    dict_["embedding"]
                )

            if "lion_class" in dict_:
                cls = _init_class.get(dict_.pop("lion_class"), cls)

            if "lc" in dict_:
                dict_ = cls._process_langchain_dict(dict_)
            else:
                dict_ = cls._process_generic_dict(dict_)

            return cls.model_validate(dict_, *args, **kwargs)

        except ValidationError as e:
            raise LionValueError(
                "Invalid dictionary for deserialization."
            ) from e

    @classmethod
    def _process_langchain_dict(cls, dict_: dict) -> dict:
        """Process a dictionary containing Langchain-specific data."""
        change_dict_key(dict_, "page_content", "content")

        metadata = dict_.pop("metadata", {})
        metadata.update(dict_.pop("kwargs", {}))

        if not isinstance(metadata, dict):
            metadata = {"extra_meta": metadata}

        for field in base_lion_fields:
            if field in metadata:
                dict_[field] = metadata.pop(field)

        for key in list(metadata.keys()):
            if key not in lc_meta_fields:
                dict_[key] = metadata.pop(key)

        for field in lc_meta_fields:
            if field in dict_:
                metadata[field] = dict_.pop(field)

        change_dict_key(metadata, "lc", "langchain")
        change_dict_key(metadata, "type", "lc_type")
        change_dict_key(metadata, "id", "lc_id")

        extra_fields = {
            k: v for k, v in metadata.items() if k not in lc_meta_fields
        }
        metadata = {k: v for k, v in metadata.items() if k in lc_meta_fields}
        dict_["metadata"] = metadata
        dict_.update(extra_fields)

        return dict_

    @classmethod
    def _process_generic_dict(cls, dict_: dict) -> dict:
        """Process a generic dictionary."""
        meta_ = dict_.pop("metadata", None) or {}

        if not isinstance(meta_, dict):
            meta_ = {"extra_meta": meta_}

        for key in list(dict_.keys()):
            if key not in base_lion_fields:
                meta_[key] = dict_.pop(key)

        if not dict_.get("content", None):
            for field in ["page_content", "text", "chunk_content", "data"]:
                if field in meta_:
                    dict_["content"] = meta_.pop(field)
                    break

        dict_["metadata"] = meta_

        if "ln_id" not in dict_:
            dict_["ln_id"] = meta_.pop("ln_id", SysUtil.id())
        if "timestamp" not in dict_:
            dict_["timestamp"] = ln.time(type_="iso")
        if "metadata" not in dict_:
            dict_["metadata"] = {}
        if "extra_fields" not in dict_:
            dict_["extra_fields"] = {}

        return dict_

    @classmethod
    def _from_str(
        cls, obj: str, /, *args, fuzzy_parse: bool = False, **kwargs
    ) -> T:
        """Create a Component instance from a JSON string."""
        obj = ParseUtil.fuzzy_parse_json(obj) if fuzzy_parse else to_dict(obj)
        try:
            return cls.from_obj(obj, *args, **kwargs)
        except ValidationError as e:
            raise LionValueError("Invalid JSON for deserialization: ") from e

    @classmethod
    def _from_list(cls, obj: list, /, *args, **kwargs) -> list[T]:
        """Create a list of node instances from a list of objects."""
        return [cls.from_obj(item, *args, **kwargs) for item in obj]

    @classmethod
    def _from_pd_series(
        cls, obj: Series, /, *args, pd_kwargs: dict | None = None, **kwargs
    ) -> T:
        """Create a node instance from a Pandas Series."""
        pd_kwargs = pd_kwargs or {}
        return cls.from_obj(obj.to_dict(**pd_kwargs), *args, **kwargs)

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

    @property
    def class_name(self) -> str:
        """Get the class name."""
        return self._class_name()

    @classmethod
    def _class_name(cls) -> str:
        """Get the class name."""
        return cls.__name__

    def to_json_str(self, *args, dropna=False, **kwargs) -> str:
        """Convert the component to a JSON string."""
        dict_ = self.to_dict(*args, dropna=dropna, **kwargs)
        return to_str(dict_)

    def to_dict(self, *args, dropna=False, **kwargs) -> dict[str, Any]:
        """Convert the component to a dictionary."""
        dict_ = self.model_dump(*args, by_alias=True, **kwargs)

        for field_name in list(self.extra_fields.keys()):
            if field_name not in dict_:
                dict_[field_name] = getattr(self, field_name, None)

        dict_.pop("extra_fields", None)
        dict_["lion_class"] = self.class_name
        if dropna:
            dict_ = {k: v for k, v in dict_.items() if v is not None}
        return dict_

    def to_xml(self, *args, dropna=False, **kwargs) -> str:
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

        convert(self.to_dict(*args, dropna=dropna, **kwargs), root)
        return ET.tostring(root, encoding="unicode")

    def to_pd_series(
        self, *args, pd_kwargs=None, dropna=False, **kwargs
    ) -> Series:
        """Convert the node to a Pandas Series."""
        pd_kwargs = pd_kwargs or {}
        dict_ = self.to_dict(*args, dropna=dropna, **kwargs)
        return Series(dict_, **pd_kwargs)

    def to_llama_index_node(
        self, node_type: type | str | Any = None, **kwargs
    ) -> Any:
        """Serializes this node for LlamaIndex."""
        from lionagi.integrations.bridge import LlamaIndexBridge

        return LlamaIndexBridge.to_llama_index_node(
            self, node_type=node_type, **kwargs
        )

    def to_langchain_doc(self, **kwargs) -> Any:
        """Serializes this node for Langchain."""
        from lionagi.integrations.bridge import LangchainBridge

        return LangchainBridge.to_langchain_document(self, **kwargs)

    def _add_last_update(self, name):
        if (a := nget(self.metadata, ["last_updated", name], None)) is None:
            ninsert(
                self.metadata,
                ["last_updated", name],
                ln.time(type_="iso")[:-6],
            )
        elif isinstance(a, tuple) and isinstance(a[0], int):
            nset(
                self.metadata,
                ["last_updated", name],
                ln.time(type_="iso")[:-6],
            )

    def _meta_pop(self, indices, default=...):
        indices = (
            indices
            if not isinstance(indices, list)
            else "[^_^]".join([str(i) for i in indices])
        )
        dict_ = self.metadata.copy()
        dict_ = flatten(dict_)

        try:
            out_ = (
                dict_.pop(indices, default)
                if default != ...
                else dict_.pop(indices)
            )
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

    def _meta_get(self, indices, default=...):
        if default != ...:
            return nget(self.metadata, indices=indices, default=default)
        return nget(self.metadata, indices)

    def __setattr__(self, name, value):
        if name == "metadata":
            raise AttributeError("Cannot directly assign to metadata.")
        super().__setattr__(name, value)
        self._add_last_update(name)

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
        self.extra_fields[field] = field_obj or Field(
            default=default, **kwargs
        )
        if annotation:
            self.extra_fields[field].annotation = annotation

        if not value and (a := self._get_field_attr(field, "default", None)):
            value = a

        self.__setattr__(field, value)

    def add_field(self, field, value, annotation=None, **kwargs):
        self._add_field(field, annotation, value=value, **kwargs)

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
                raise FieldError(f"field {k} has no attribute {attr}")

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
                dict_[k] = [v.__name__] if v else None
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

        if attr not in str(field):
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
        return Series(dict_).__str__()

    def __repr__(self):
        dict_ = self.to_dict()
        return Series(dict_).__repr__()

    def __len__(self):
        return 1


LionIDable: TypeAlias = Union[str, Element]


def get_lion_id(item: LionIDable) -> str:
    """Get the Lion ID of an item."""
    return SysUtil.get_id(item)
