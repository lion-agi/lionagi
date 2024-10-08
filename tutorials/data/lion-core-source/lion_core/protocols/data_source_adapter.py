from collections.abc import Callable
from pathlib import Path

from lionfuncs import read_file, save_to_file

from lion_core.protocols.adapter import Adapter
from lion_core.protocols.data_adapter import DataAdapter, JsonDataAdapter


class DataSourceAdapterConfig:

    data_adapter: DataAdapter

    save_func: Callable
    save_config: dict = {}

    read_func: Callable
    read_config: dict = {}

    def __init__(
        self,
        data_adapter: DataAdapter,
        save_func: Callable = save_to_file,
        save_config: dict = {},
        read_func: Callable = read_file,
        read_config: dict = {},
    ):
        self.data_adapter = data_adapter
        self.save_func = save_func
        self.save_config = save_config
        self.read_func = read_func
        self.read_config = read_config


class DataSourceAdapter(Adapter):

    config: DataSourceAdapterConfig

    @classmethod
    def from_obj(cls, subj_cls, obj, **kwargs) -> dict:
        """
        kwargs for read_func
        """
        kwargs = {**cls.config.read_config, **kwargs}
        obj = cls.config.read_func(obj, **kwargs)
        return cls.config.data_adapter.from_obj(subj_cls, obj)

    @classmethod
    def to_obj(cls, subj, **kwargs) -> str:
        """
        kwargs for save_func
        """
        kwargs = {**cls.config.save_config, **kwargs}
        obj = cls.config.data_adapter.to_obj(subj)
        return cls.config.save_func(obj, **kwargs)


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


class JsonFileAdapter(DataSourceAdapter):

    obj_key = "json_file"
    verbose = False
    config = json_file_config


__all__ = ["JsonFileAdapter", "DataSourceAdapter"]
