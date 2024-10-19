from pathlib import Path
from typing import Any

from lion_core.generic.component import Component
from lion_core.protocols.data_source_adapter import (
    DataSourceAdapter,
    DataSourceAdapterConfig,
)
from lionfuncs import read_file, save_to_file, to_csv, to_excel
from pandas import DataFrame, read_csv, read_excel

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


class CSVFileAdapter(DataSourceAdapter):
    obj_key = "csv_file"
    verbose = False
    config = None

    @classmethod
    def from_obj(cls, subj_cls, obj: Any, /, **kwargs) -> dict:
        """kwargs for pandas.read_csv"""
        df: DataFrame = read_csv(obj, **kwargs)
        return df.to_dict(orient="records", index=False)

    @classmethod
    def to_obj(
        cls,
        subj: Component,
        /,
        directory: str | Path = Path(".") / "data" / "csv_files",
        filename: str = "unnamed_csv_file",
        timestamp: bool = True,
        random_hash_digits: int = 4,
        drop_how: str = "all",
        drop_kwargs: dict | None = None,
        reset_index: bool = True,
        concat_kwargs: dict | None = None,
        df_kwargs: dict = None,
        path_kwargs: dict = None,
    ):

        to_csv(
            subj.to_dict(),
            directory=directory,
            filename=filename,
            timestamp=timestamp,
            random_hash_digits=random_hash_digits,
            drop_how=drop_how,
            drop_kwargs=drop_kwargs,
            reset_index=reset_index,
            concat_kwargs=concat_kwargs,
            df_kwargs=df_kwargs,
            path_kwargs=path_kwargs,
            verbose=cls.verbose,
        )


class ExcelFileAdapter(DataSourceAdapter):
    obj_key = "excel_file"
    verbose = False
    config = None

    @classmethod
    def from_obj(cls, subj_cls, obj: Any, /, **kwargs) -> dict:
        """kwargs for pandas.read_csv"""
        df: DataFrame = read_excel(obj, **kwargs)
        return df.to_dict(orient="records", index=False)

    @classmethod
    def to_obj(
        cls,
        subj: Component,
        /,
        directory: str | Path = Path(".") / "data" / "excel_files",
        filename: str = "unnamed_excel_file",
        timestamp: bool = True,
        random_hash_digits: int = 4,
        drop_how: str = "all",
        drop_kwargs: dict | None = None,
        reset_index: bool = True,
        concat_kwargs: dict | None = None,
        df_kwargs: dict = None,
        path_kwargs: dict = None,
    ):

        to_excel(
            subj.to_dict(),
            directory=directory,
            filename=filename,
            timestamp=timestamp,
            random_hash_digits=random_hash_digits,
            drop_how=drop_how,
            drop_kwargs=drop_kwargs,
            reset_index=reset_index,
            concat_kwargs=concat_kwargs,
            df_kwargs=df_kwargs,
            path_kwargs=path_kwargs,
            verbose=cls.verbose,
        )
