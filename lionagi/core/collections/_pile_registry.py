import json

from lion_core.protocols.data_adapter import DataAdapter, DataAdapterConfig

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
    to_obj_parser=lambda x: to_str(x.to_dict(), **kwargs),
    to_obj_config={
        "use_model_dump": False,
        "serialize_as": "json",
        "strip_lower": False,
        "chars": None,  # additional kwargs for json.dumps
    },
)
