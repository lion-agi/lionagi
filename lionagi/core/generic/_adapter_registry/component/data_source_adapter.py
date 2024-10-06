from pathlib import Path

from lion_core.protocols.data_source_adapter import (
    DataSourceAdapter,
    DataSourceAdapterConfig,
)
from lionfuncs import read_file, save_to_file

from .data_adapter import JsonDataAdapter, XMLDataAdapter

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


class JsonFileAdapter(DataSourceAdapter):

    obj_key = "json_file"
    verbose = False
    config = json_file_config


class XMLFileAdapter(DataSourceAdapter):

    obj_key = "xml_file"
    verbose = False
    config = xml_file_config
