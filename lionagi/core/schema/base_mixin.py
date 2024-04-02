from abc import ABC
from functools import singledispatchmethod
from typing import Any, TypeVar, Type, Callable

import pandas as pd
from pydantic import BaseModel, ValidationError

from lionagi.libs import nested, convert, ParseUtil, SysUtil

T = TypeVar("T")  # Generic type for return type of from_obj method


class BaseToObjectMixin(ABC, BaseModel):

    def to_json_str(self, *args, **kwargs) -> str:
        """
        Serializes the model instance into a JSON string.

        This method utilizes the model's `model_dump_json` method, typically available in Pydantic
        models or models with similar serialization mechanisms, to convert the instance into a JSON
        string. It supports passing arbitrary arguments to the underlying `model_dump_json` method.

        Args:
                *args: Variable-length argument list to be passed to `model_dump_json`.
                **kwargs: Arbitrary keyword arguments, with `by_alias=True` set by default to use
                                  model field aliases in the output JSON, if any.

        Returns:
                str: A JSON string representation of the model instance.
        """
        return self.model_dump_json(*args, by_alias=True, **kwargs)

    def to_dict(self, *args, **kwargs) -> dict[str, Any]:
        """
        Converts the model instance into a dictionary.

        Leveraging the model's `model_dump` method, this function produces a dictionary representation
        of the model. The dictionary keys correspond to the model's field names, with an option to use
        aliases instead of the original field names.

        Args:
                *args: Variable-length argument list for the `model_dump` method.
                **kwargs: Arbitrary keyword arguments. By default, `by_alias=True` is applied, indicating
                                  that field aliases should be used as keys in the resulting dictionary.

        Returns:
                dict[str, Any]: The dictionary representation of the model instance.
        """
        return self.model_dump(*args, by_alias=True, **kwargs)

    def to_xml(self) -> str:
        """
        Serializes the model instance into an XML string.

        This method converts the model instance into an XML format. It first transforms the instance
        into a dictionary and then recursively constructs an XML tree representing the model's data.
        The root element of the XML tree is named after the class of the model instance.

        Returns:
                str: An XML string representation of the model instance.
        """

        import xml.etree.ElementTree as ET

        root = ET.Element(self.__class__.__name__)

        def convert(dict_obj, parent):
            for key, val in dict_obj.items():
                if isinstance(val, dict):
                    element = ET.SubElement(parent, key)
                    convert(val, element)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(val)

        convert(self.to_dict(), root)
        return ET.tostring(root, encoding="unicode")

    def to_pd_series(self, *args, pd_kwargs: dict | None = None, **kwargs) -> pd.Series:
        """
        Converts the model instance into a pandas Series.

        This method first transforms the model instance into a dictionary and then constructs a pandas
        Series from it. The Series' index corresponds to the model's field names, with an option to
        customize the Series creation through `pd_kwargs`.

        Args:
                *args: Variable-length argument list for the `to_dict` method.
                pd_kwargs (dict | None): Optional dictionary of keyword arguments to pass to the pandas
                                                                 Series constructor. Defaults to None, in which case an empty
                                                                 dictionary is used.
                **kwargs: Arbitrary keyword arguments for the `to_dict` method, influencing the dictionary
                                  representation used for Series creation.

        Returns:
                pd.Series: A pandas Series representation of the model instance.
        """
        pd_kwargs = {} if pd_kwargs is None else pd_kwargs
        dict_ = self.to_dict(*args, **kwargs)
        return pd.Series(dict_, **pd_kwargs)


class BaseFromObjectMixin(ABC, BaseModel):

    @singledispatchmethod
    @classmethod
    def from_obj(cls: Type[T], obj: Any, *args, **kwargs) -> T:
        raise NotImplementedError(f"Unsupported type: {type(obj)}")

    @from_obj.register(dict)
    @classmethod
    def _from_dict(cls, obj: dict, *args, **kwargs) -> T:
        return cls.model_validate(obj, *args, **kwargs)

    @from_obj.register(str)
    @classmethod
    def _from_str(cls, obj: str, *args, fuzzy_parse=False, **kwargs) -> T:
        obj = ParseUtil.fuzzy_parse_json(obj) if fuzzy_parse else convert.to_dict(obj)
        try:
            return cls.from_obj(obj, *args, **kwargs)
        except ValidationError as e:
            raise ValueError(f"Invalid JSON for deserialization: {e}") from e

    @from_obj.register(list)
    @classmethod
    def _from_list(cls, obj: list[Any], *args, **kwargs) -> list[T]:
        return [cls.from_obj(item, *args, **kwargs) for item in obj]

    @from_obj.register(pd.Series)
    @classmethod
    def _from_pd_series(cls, obj: pd.Series, *args, pd_kwargs=None, **kwargs) -> T:
        if pd_kwargs is None:
            pd_kwargs = {}
        return cls.from_obj(obj.to_dict(**pd_kwargs), *args, **kwargs)

    @from_obj.register(pd.DataFrame)
    @classmethod
    def _from_pd_dataframe(
        cls, obj: pd.DataFrame, *args, pd_kwargs=None, **kwargs
    ) -> list[T]:
        if pd_kwargs is None:
            pd_kwargs = {}
        return [
            cls.from_obj(row, *args, **pd_kwargs, **kwargs) for _, row in obj.iterrows()
        ]

    @from_obj.register(BaseModel)
    @classmethod
    def _from_base_model(cls, obj: BaseModel, pydantic_kwargs=None, **kwargs) -> T:
        if pydantic_kwargs is None:
            pydantic_kwargs = {"by_alias": True}
        config_ = {**obj.model_dump(**pydantic_kwargs), **kwargs}
        return cls.from_obj(**config_)


class BaseMetaManageMixin(ABC, BaseModel):

    def meta_keys(self, flattened: bool = False, **kwargs) -> list[str]:
        """
        Retrieves a list of metadata keys.

        Args:
                flattened (bool): If True, returns keys from a flattened metadata structure.
                **kwargs: Additional keyword arguments passed to the flattening function.

        Returns:
                list[str]: List of metadata keys.
        """
        if flattened:
            return nested.get_flattened_keys(self.metadata, **kwargs)
        return list(self.metadata.keys())

    def meta_has_key(self, key: str, flattened: bool = False, **kwargs) -> bool:
        """
        Checks if a specified key exists in the metadata.

        Args:
                key (str): The key to check.
                flattened (bool): If True, checks within a flattened metadata structure.
                **kwargs: Additional keyword arguments for flattening.

        Returns:
                bool: True if key exists, False otherwise.
        """
        if flattened:
            return key in nested.get_flattened_keys(self.metadata, **kwargs)
        return key in self.metadata

    def meta_get(
        self, key: str, indices: list[str | int] = None, default: Any = None
    ) -> Any:
        """
        Retrieves the value associated with a given key from the metadata.

        Args:
                key (str): The key for the desired value.
                indices: Optional indices for nested retrieval.
                default (Any): The default value to return if the key is not found.

        Returns:
                Any: The value associated with the key or the default value.
        """
        if indices:
            return nested.nget(self.metadata, key, indices, default)
        return self.metadata.get(key, default)

    def meta_change_key(self, old_key: str, new_key: str) -> bool:
        """
        Renames a key in the metadata.

        Args:
                old_key (str): The current key name.
                new_key (str): The new key name.

        Returns:
                bool: True if the key was changed, False otherwise.
        """
        if old_key in self.metadata:
            SysUtil.change_dict_key(self.metadata, old_key, new_key)
            return True
        return False

    def meta_insert(self, indices: str | list, value: Any, **kwargs) -> bool:
        """
        Inserts a value into the metadata at specified indices.

        Args:
                indices (str | list): The indices where the value should be inserted.
                value (Any): The value to insert.
                **kwargs: Additional keyword arguments.

        Returns:
                bool: True if the insertion was successful, False otherwise.
        """
        return nested.ninsert(self.metadata, indices, value, **kwargs)

    # ToDo: do a nested pop
    def meta_pop(self, key: str, default: Any = None) -> Any:
        """
        Removes a key from the metadata and returns its value.

        Args:
                key (str): The key to remove.
                default (Any): The default value to return if the key is not found.

        Returns:
                Any: The value of the removed key or the default value.
        """
        return self.metadata.pop(key, default)

    def meta_merge(
        self, additional_metadata: dict[str, Any], overwrite: bool = False, **kwargs
    ) -> None:
        """
        Merges additional metadata into the existing metadata.

        Args:
                additional_metadata (dict[str, Any]): The metadata to merge in.
                overwrite (bool): If True, existing keys will be overwritten by those in additional_metadata.
                **kwargs: Additional keyword arguments for the merge.

        Returns:
                None
        """
        nested.nmerge(
            [self.metadata, additional_metadata], overwrite=overwrite, **kwargs
        )

        for key, value in additional_metadata.items():
            if overwrite or key not in self.metadata:
                self.metadata[key] = value

    def meta_clear(self) -> None:
        """
        Clears all metadata.

        Returns:
                None
        """
        self.metadata.clear()

    def meta_filter(self, condition: Callable[[Any, Any], bool]) -> dict[str, Any]:
        """
        Filters the metadata based on a condition.

        Args:
                condition (Callable[[Any, Any], bool]): The condition function to apply.

        Returns:
                dict[str, Any]: The filtered metadata.
        """
        return nested.nfilter(self.metadata, condition)


class BaseComponentMixin(BaseFromObjectMixin, BaseToObjectMixin, BaseMetaManageMixin):
    pass
