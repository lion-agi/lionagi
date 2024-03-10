from abc import ABC
from typing import Any, TypeVar

import pandas as pd
from pydantic import BaseModel


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
