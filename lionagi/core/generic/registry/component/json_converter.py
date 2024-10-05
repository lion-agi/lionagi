import json

from typing import Callable
from lionfuncs import to_dict, to_str

from lion_core.protocols.adapter import Adapter
from lion_core.generic.note import Note
from lion_core.generic.base import RealElement

from pydantic import BaseModel


class DataAdapterConfig:
    
    from_obj_parser: Callable   # need to return a dict
    from_obj_config: dict
    to_obj_parser: Callable
    to_obj_config: dict
    
    def __init__(self, from_obj_parser, from_obj_config, to_obj_parser, to_obj_config):
        self.from_obj_parser = from_obj_parser
        self.from_obj_config = from_obj_config
        self.to_obj_parser = to_obj_parser
        self.to_obj_config = to_obj_config
    
    def to_note(self):
        return Note(
            **{
                "from": {
                    "parser": self.from_obj_parser,
                    "config": self.from_obj_config
                },
                "to": {
                    "parser": self.to_obj_parser,
                    "config": self.to_obj_config
                }
            }
        )
    

json_config = DataAdapterConfig(
    from_obj_parser=to_dict,
    from_obj_config={},
    to_obj_parser=json.dumps,
    to_obj_config={}
)








class JsonDataAdapter(Adapter):
    
    obj_key = "json_data"
    verbose = False
    config = json_config

    @classmethod
    def from_obj(cls, subj_cls: type[RealElement], obj, **kwargs) -> dict:
        kwargs = {**cls.config["from", "config"], **kwargs}
        return cls.config["from", "parser"](obj, **kwargs)
        
    @classmethod
    def to_obj(cls, subj: RealElement, **kwargs) -> str:
        kwargs = {**cls.config["to", "config"], **kwargs}
        return cls.config["to", "parser"](subj.to_dict(), **kwargs)


    @classmethod
    def from_obj(cls, subj_cls, obj, **kwargs):
        kwargs = {**cls.config, **kwargs}
        return to_dict(obj, **kwargs)

    @classmethod
    def to_obj(cls, subj, **kwargs):
        dict_ = subj.to_dict()
        return json.dumps(dict_, **kwargs)


class JsonFileAdapter(Adapter):

    ...
    
    
class JsonlFileAdapter(Adapter):

    ...
    
    


















import json
from pathlib import Path
from typing import Any, TypeVar

from lion_core.generic.component import Component
from lion_core.converter import Converter
from lionfuncs import save_to_file, to_dict

T = TypeVar("T", bound=Component)


class JsonConverter(Converter):

    obj_key = "json"

    @classmethod
    def to_obj(
        cls,
        subj: Component,
        /,
        **kwargs: Any,
    ) -> str:
        dict_ = subj.to_dict()
        return json.dumps(dict_, **kwargs)
    
    @classmethod
    def from_obj(
        cls,
        subj_cls: type[Component],
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict:
        """
        obj should be a path to json file
        kwargs for json.load
        """
        dict_ = json.load(obj)
        return to_dict(dict_**kwargs)
    
class JsonFileConverter(Converter):

    obj_key = ".json"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[Component],
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict:
        return json.load(obj, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        fp=None,
        **kwargs: Any,
    ) -> str | Path:
        
        if not fp:
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
