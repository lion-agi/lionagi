from typing import Callable
from lionfuncs import to_dict, to_str
from lion_core.protocols.adapter import Adapter
from lion_core.generic.note import Note
from lion_core.generic.base import RealElement
from pandas import Series

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
    

class DataAdapter(Adapter):

    config: Note

    @classmethod
    def from_obj(cls, subj_cls: type[RealElement], obj, **kwargs) -> dict:
        kwargs = {**cls.config["from", "config"], **kwargs}
        return cls.config["from", "parser"](obj, **kwargs)
        
    @classmethod
    def to_obj(cls, subj: RealElement, **kwargs) -> str:
        subj = subj.to_dict()
        kwargs = {**cls.config["to", "config"], **kwargs}
        return cls.config["to", "parser"](subj, **kwargs)
    
    
json_data_config = DataAdapterConfig(
    from_obj_parser=to_dict,
    from_obj_config={
        "fuzzy_parse": False,
        "str_type": "json",
        "suppress": False,
        "recursive": False,
        "max_recursive_depth": 1,
        "recursive_python_only": True,
        "exclude_types": (),
        "recursive_custom_types": False,      # additional kwargs for json.loads
    },
    to_obj_parser=to_str,
    to_obj_config={
        "use_model_dump": False,
        "serialize_as": "json",
        "strip_lower": False,
        "chars": None,  # additional kwargs for json.dumps
    },
)

xml_data_config = DataAdapterConfig(
    from_obj_parser=to_dict,
    from_obj_config={
        "str_type": "xml",
        "suppress": False,
        "root_tag": "root",
        "remove_root": True,
    },
    to_obj_parser=to_str,
    to_obj_config={
        "root_tag": "root",
        "use_model_dump": False,
        "serialize_as": "xml",
        "strip_lower": False,
        "chars": None,
    }
)

pd_series_data_config = DataAdapterConfig(
    from_obj_parser=to_dict,
    from_obj_config={
        "suppress": False,
        "recursive": False,
        "max_recursive_depth": 1,
        "recursive_python_only": True,
        "exclude_types": (),
        "recursive_custom_types": False,        # additional kwargs for pd.Series.to_dict
    },
    to_obj_parser=Series,
    to_obj_config={},  # additional kwargs for pd.Series
)

class JsonDataAdapter(Adapter):
    
    obj_key = "json_data"
    verbose = False
    config = json_data_config.to_note()
    
    
class XMLDataAdapter(Adapter):
        
    obj_key = "xml_data"
    verbose = False
    config = xml_data_config.to_note()
    
class PandasSeriesAdapter(Adapter):
    
    obj_key = "pd_series"
    verbose = False
    config = pd_series_data_config.to_note()