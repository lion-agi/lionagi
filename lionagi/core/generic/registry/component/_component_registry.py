import json
from pathlib import Path
from typing import Any, TypeVar

import pandas as pd
from lion_core.protocols.adapter import Adapter, AdapterRegistry



from lion_core.converter import Converter, ConverterRegistry
from lion_core.generic.base import RealElement
from lionfuncs import check_import, dict_to_xml, save_to_file, to_dict

from lionagi.integrations.bridge.langchain_.converter import LangChainConverter
from lionagi.integrations.bridge.llamaindex_.converter import LlamaIndexConverter

T = TypeVar("T", bound=RealElement)


class JsonConverter(Converter):

    obj_key = "json"

    @classmethod
    def from_obj(
        cls,
        subj_cls,
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict:
        """
        kwargs for to_dict
        """
        return to_dict(obj, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> str:
        """
        kwargs for json.dumps
        """
        dict_ = subj.to_dict()
        return json.dumps(dict_, **kwargs)


class JsonFileConverter(Converter):

    obj_key = ".json"








class JsonFileConverter(Converter):

    obj_key = ".json"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[RealElement],
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict:
        """
        obj should be a path to json file
        kwargs for json.load
        """
        return json.load(obj, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> str | Path:
        """
        kwargs for save_to_file,
        return the path of the file
        """
        if "fp" not in kwargs:
            if "directory" not in kwargs:
                kwargs["directory"] = "./data/json_files"
            if "filename" not in kwargs:
                kwargs["filename"] = f"{subj.ln_id[:5]}.json"
            try:
                return save_to_file(json.dumps(subj.to_dict(), **kwargs))
            except FileExistsError:
                kwargs["timestamp"] = True
                return save_to_file(json.dumps(subj.to_dict(), **kwargs))
        json.dump(subj.to_dict(), fp=kwargs["fp"])
        return kwargs["fp"]


class XMLConverter(Converter):

    obj_key = "xml"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[RealElement],
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict:
        """
        obj should be a path to json file
        kwargs for to_dict
        """
        kwargs["str_type"] = "xml"
        return to_dict(obj, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> str:
        dict_ = subj.to_dict()
        if "root_tag" in kwargs:
            return dict_to_xml(dict_, root_tag=kwargs["root_tag"])
        return dict_to_xml(dict_)


class XMLFileConverter(Converter):

    obj_key = ".xml"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[RealElement],
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        obj should be a path to json file
        kwargs for to_dict
        """
        kwargs["str_type"] = "xml"
        with open(obj, "r") as file:
            return to_dict(file.read(), **kwargs)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> Any:
        if "directory" not in kwargs:
            kwargs["directory"] = "./data/xml_files"
        if "filename" not in kwargs:
            kwargs["filename"] = f"{subj.ln_id[:5]}.xml"
        try:
            return save_to_file(json.dumps(subj.to_dict()), **kwargs)
        except FileExistsError:
            kwargs["timestamp"] = True
            return save_to_file(json.dumps(subj.to_dict(), **kwargs))


class PandasSeriesConverter(Converter):

    obj_key = "pd_series"
    Series = check_import("pandas", import_name="Series")

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[RealElement],
        obj: pd.Series,
        /,
        **kwargs: pd.Series,
    ) -> dict[str, Any]:
        return obj.to_dict()

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> Any:
        dict_ = subj.to_dict()
        return cls.Series(dict_)


class ComponentConverterRegistry(ConverterRegistry):
    pass


ComponentConverterRegistry.register(JsonConverter)
ComponentConverterRegistry.register(JsonFileConverter)
ComponentConverterRegistry.register(XMLConverter)
ComponentConverterRegistry.register(XMLFileConverter)
ComponentConverterRegistry.register(PandasSeriesConverter)
ComponentConverterRegistry.register(LangChainConverter)
ComponentConverterRegistry.register(LlamaIndexConverter)

__all__ = ["ComponentConverterRegistry"]
