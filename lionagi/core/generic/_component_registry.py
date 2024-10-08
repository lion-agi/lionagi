import json
from pathlib import Path

import pandas as pd
from lion_core.protocols.adapter import AdapterRegistry
from lion_core.protocols.data_adapter import DataAdapter, DataAdapterConfig
from lion_core.protocols.data_source_adapter import (
    DataSourceAdapter,
    DataSourceAdapterConfig,
)
from lionfuncs import create_path, read_file, save_to_file, to_dict, to_str

from lionagi.integrations.bridge.langchain_.adapter import (
    LangChainDocumentAdapter,
)
from lionagi.integrations.bridge.llamaindex_.adapter import (
    LlamaIndexNodeAdapter,
)

dict_data_config = DataAdapterConfig(
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
    to_obj_parser=to_dict,
    to_obj_config={
        "use_model_dump": False,
    },
)

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


def pd_to_dict(input: pd.Series | pd.DataFrame, **kwargs):
    dict_ = input.to_dict()
    return to_dict(dict_, **kwargs)


pd_series_data_config = DataAdapterConfig(
    from_obj_parser=pd_to_dict,
    from_obj_config={
        "suppress": False,
        "recursive": False,
        "max_recursive_depth": 1,
        "recursive_python_only": True,
        "exclude_types": (),
        "recursive_custom_types": False,  # additional kwargs for pd.Series.to_dict
    },
    to_obj_parser=pd.Series,
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
    to_obj_parser=pd.DataFrame,
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


class DictDataAdapter(DataAdapter):

    obj_key = "dict_data"
    verbose = False
    config = dict_data_config


json_file_config = DataSourceAdapterConfig(
    data_adapter=JsonDataAdapter,
    save_func=save_to_file,
    save_config={
        "directory": Path(".") / "data" / "json_files",
        "filename": "unnamed_json_file",
        "extension": ".json",
        "timestamp": True,
        "random_hash_digits": 4,
    },
    read_func=read_file,
    read_config={},
)

xml_file_config = DataSourceAdapterConfig(
    data_adapter=XMLDataAdapter,
    save_func=save_to_file,
    save_config={
        "directory": Path(".") / "data" / "xml_files",
        "filename": "unnamed_xml_file",
        "extension": ".xml",
        "timestamp": True,
        "random_hash_digits": 4,
    },
    read_func=read_file,
    read_config={},
)


def save_csv(input: pd.DataFrame | pd.Series, **kwargs):
    fp = create_path(**kwargs)
    input.to_csv(fp, index=False)


def save_excel(input: pd.DataFrame | pd.Series, **kwargs):
    fp = create_path(**kwargs)
    input.to_excel(fp, index=False)


def save_jsonl(input: dict, **kwargs):
    json_line = json.dumps(input) + "\n"
    save_to_file(json_line, **kwargs)


def read_jsonl(input: str, **kwargs):
    a = read_file(input).strip()
    if a.endswith("\n"):
        a = a[:-1]
    return json.loads(a, **kwargs)


csv_file_config = DataSourceAdapterConfig(
    data_adapter=PandasDataFrameDataAdapter,
    save_func=save_csv,
    save_config={
        "directory": Path(".") / "data" / "csv_files",
        "filename": "unnamed_csv_file",
        "timestamp": True,
        "random_hash_digits": 4,
        "extension": ".csv",
    },
    read_func=pd.read_csv,
    read_config={},
)

excel_file_config = DataSourceAdapterConfig(
    data_adapter=PandasDataFrameDataAdapter,
    save_func=save_excel,
    save_config={
        "directory": Path(".") / "data" / "excel_files",
        "filename": "unnamed_excel_file",
        "timestamp": True,
        "random_hash_digits": 4,
        "extension": ".xlsx",
    },
    read_func=pd.read_excel,
    read_config={},
)

jsonl_file_config = DataSourceAdapterConfig(
    data_adapter=DictDataAdapter,
    save_func=save_jsonl,
    save_config={
        "directory": Path(".") / "data" / "jsonl_files",
        "filename": "unnamed_jsonl_file",
        "timestamp": True,
        "random_hash_digits": 4,
        "extension": ".jsonl",
    },
    read_func=read_jsonl,
    read_config={},
)


class JsonFileAdapter(DataSourceAdapter):

    obj_key = "json_file"
    verbose = False
    config = json_file_config


class XMLFileAdapter(DataSourceAdapter):

    obj_key = "xml_file"
    verbose = False
    config = xml_file_config


class CSVFileAdapter(DataSourceAdapter):

    obj_key = "csv_file"
    verbose = False
    config = csv_file_config


class ExcelFileAdapter(DataSourceAdapter):

    obj_key = "excel_file"
    verbose = False
    config = excel_file_config


class JSONLFileAdapter(DataSourceAdapter):

    obj_key = "jsonl_file"
    verbose = False
    config = jsonl_file_config


class ComponentAdapterRegistry(AdapterRegistry): ...


adapters = [
    JsonDataAdapter,  # json_data
    XMLDataAdapter,  # xml_data
    PandasSeriesDataAdapter,  # pd_series_data
    PandasDataFrameDataAdapter,  # pd_df_data
    DictDataAdapter,  # dict_data
    JsonFileAdapter,  # json_file
    XMLFileAdapter,  # xml_file
    CSVFileAdapter,  # csv_file
    ExcelFileAdapter,  # excel_file
    JSONLFileAdapter,  # jsonl_file
    LangChainDocumentAdapter,  # langchain_doc
    LlamaIndexNodeAdapter,  # llamaindex_node
]

for i in adapters:
    ComponentAdapterRegistry.register(i)

__all__ = ["ComponentAdapterRegistry"]
