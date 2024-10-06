from lion_core.protocols.data_adapter import DataAdapter, DataAdapterConfig
from lionfuncs import to_dict, to_str
from pandas import DataFrame, Series

json_data_config = DataAdapterConfig(
    from_obj_parser=to_dict,
    from_obj_config={
        "fuzzy_parse": False,
        "str_type": "json",
        "suppress": False,
        "recursive": True,
        "max_recursive_depth": 5,
        "recursive_python_only": True,
        "exclude_types": (),  # additional kwargs for json.loads
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
        "fuzzy_parse": False,
        "str_type": "xml",
        "suppress": False,
    },
    to_obj_parser=to_str,
    to_obj_config={
        "use_model_dump": False,
        "serialize_as": "xml",
        "strip_lower": False,
        "chars": None,
    },
)

pd_series_data_config = DataAdapterConfig(
    from_obj_parser=to_dict,
    from_obj_config={
        "suppress": False,
        "recursive": False,
        "max_recursive_depth": 1,
        "recursive_python_only": True,
        "exclude_types": (),
        "recursive_custom_types": False,  # additional kwargs for pd.Series.to_dict
    },
    to_obj_parser=Series,
    to_obj_config={},  # additional kwargs for pd.Series
)

pd_df_data_config = DataAdapterConfig(
    from_obj_parser=to_dict,
    from_obj_config={
        "suppress": False,
        "recursive": False,
        "max_recursive_depth": 1,
        "recursive_python_only": True,
        "exclude_types": (),
        "recursive_custom_types": False,  # additional kwargs for pd.DataFrame.to_dict
    },
    to_obj_parser=DataFrame,
    to_obj_config={},  # additional kwargs for pd.DataFrame
)


class JsonDataAdapter(DataAdapter):

    obj_key = "json_data"
    verbose = False
    config = json_data_config


class XMLDataAdapter(DataAdapter):

    obj_key = "xml_data"
    verbose = False
    config = xml_data_config


class PandasSeriesDataAdapter(DataAdapter):

    obj_key = "pd_series_data"
    verbose = False
    config = pd_series_data_config


class PandasDataFrameDataAdapter(DataAdapter):

    obj_key = "pd_df_data"
    verbose = False
    config = pd_df_data_config
