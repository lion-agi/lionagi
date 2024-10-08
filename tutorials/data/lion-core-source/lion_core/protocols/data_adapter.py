from collections.abc import Callable

from lionfuncs import to_dict, to_str

from lion_core.generic.base import RealElement
from lion_core.protocols.adapter import Adapter


class DataAdapterConfig:

    from_obj_parser: Callable  # need to return a dict
    from_obj_config: dict
    to_obj_parser: Callable
    to_obj_config: dict

    def __init__(
        self, from_obj_parser, from_obj_config, to_obj_parser, to_obj_config
    ):
        self.from_obj_parser = from_obj_parser
        self.from_obj_config = from_obj_config
        self.to_obj_parser = to_obj_parser
        self.to_obj_config = to_obj_config


class DataAdapter(Adapter):

    config: DataAdapterConfig

    @classmethod
    def from_obj(cls, subj_cls: type[RealElement], obj, **kwargs) -> dict:
        kwargs = {**cls.config.from_obj_config, **kwargs}
        return cls.config.from_obj_parser(obj, **kwargs)

    @classmethod
    def to_obj(cls, subj: RealElement, **kwargs) -> str:
        subj = subj.to_dict()
        kwargs = {**cls.config.to_obj_config, **kwargs}
        return cls.config.to_obj_parser(subj, **kwargs)


json_data_config = DataAdapterConfig(
    from_obj_parser=to_dict,
    from_obj_config={
        "fuzzy_parse": False,
        "str_type": "json",
        "suppress": False,
        "recursive": True,
        "max_recursive_depth": 5,
        "recursive_python_only": True,
        "exclude_types": (),
    },
    to_obj_parser=to_str,
    to_obj_config={
        "use_model_dump": False,
        "serialize_as": "json",
        "strip_lower": False,
        "chars": None,  # additional kwargs for json.dumps
    },
)


class JsonDataAdapter(DataAdapter):

    obj_key = "json_data"
    verbose = False
    config = json_data_config


__all__ = ["JsonDataAdapter", "DataAdapter"]
