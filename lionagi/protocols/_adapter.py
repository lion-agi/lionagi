# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, TypeVar, runtime_checkable

import pandas as pd
from typing_extensions import get_protocol_members

T = TypeVar("T")


@runtime_checkable
class Adapter(Protocol):

    obj_key: str

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: Any, /, **kwargs
    ) -> dict | list[dict]: ...

    @classmethod
    def to_obj(cls, subj: T, /, **kwargs) -> Any: ...


adapter_members = get_protocol_members(Adapter)  # duck typing


class AdapterRegistry:

    _adapters: dict[str, Adapter] = {}

    @classmethod
    def list_adapters(cls) -> list[tuple[str | type, ...]]:
        return list(cls._adapters.keys())

    @classmethod
    def register(cls, adapter: type[Adapter]) -> None:
        for member in adapter_members:
            if not hasattr(adapter, member):
                _str = getattr(adapter, "obj_key", None) or repr(adapter)
                _str = _str[:50] if len(_str) > 50 else _str
                raise AttributeError(
                    f"Adapter {_str} missing required methods."
                )

        if isinstance(adapter, type):
            cls._adapters[adapter.obj_key] = adapter()
        else:
            cls._adapters[adapter.obj_key] = adapter

    @classmethod
    def get(cls, obj_key: type | str) -> Adapter:
        try:
            return cls._adapters[obj_key]
        except Exception as e:
            logging.error(f"Error getting adapter for {obj_key}. Error: {e}")

    @classmethod
    def adapt_from(
        cls, subj_cls: type[T], obj: Any, obj_key: type | str, **kwargs
    ) -> dict | list[dict]:
        try:
            return cls.get(obj_key).from_obj(subj_cls, obj, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data from {obj_key}. Error: {e}")
            raise e

    @classmethod
    def adapt_to(cls, subj: T, obj_key: type | str, **kwargs) -> Any:
        try:
            return cls.get(obj_key).to_obj(subj, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data to {obj_key}. Error: {e}")
            raise e


class JsonAdapter(Adapter):

    obj_key = "json"

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: str, /) -> dict:
        return json.loads(obj)

    @classmethod
    def to_obj(cls, subj: T) -> str:
        return json.dumps(subj.to_dict())


class JsonFileAdapter(Adapter):

    obj_key = ".json"

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: str | Path, /) -> dict:
        with open(obj) as f:
            return json.load(f)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        fp: str | Path,
    ) -> None:
        with open(fp, "w") as f:
            json.dump(subj.to_dict(), f)
        logging.info(f"Successfully saved data to {fp}")


class PandasSeriesAdapter(Adapter):

    obj_key = "pd_series"
    alias = ("pandas_series", "pd.series", "pd_series")

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: pd.Series, /, **kwargs) -> dict:
        return obj.to_dict(**kwargs)

    @classmethod
    def to_obj(cls, subj: T, /, **kwargs) -> pd.Series:
        return pd.Series(subj.to_dict(), **kwargs)


class PandasDataFrameAdapter(Adapter):

    obj_key = "pd_dataframe"
    alias = ("pandas_dataframe", "pd.DataFrame", "pd_dataframe")

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: pd.DataFrame, /, **kwargs
    ) -> list[dict]:
        """kwargs for pd.DataFrame.to_dict"""
        return obj.to_dict(orient="records", **kwargs)

    @classmethod
    def to_obj(cls, subj: list[T], /, **kwargs) -> pd.DataFrame:
        """kwargs for pd.DataFrame"""
        out_ = []
        for i in subj:
            _dict = i.to_dict()
            _dict["created_at"] = datetime.fromtimestamp(_dict["created_at"])
            out_.append(_dict)
        df = pd.DataFrame(out_, **kwargs)
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
        return df


class CSVFileAdapter(Adapter):

    obj_key = ".csv"
    alias = (".csv", "csv_file", "csv")

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: str | Path, /, **kwargs
    ) -> list[dict]:
        """kwargs for pd.read_csv"""
        df = pd.read_csv(obj, **kwargs)
        return df.to_dict(orient="records")

    @classmethod
    def to_obj(
        cls,
        subj: list[T],
        /,
        fp: str | Path,
        **kwargs,
    ) -> None:
        """kwargs for pd.DataFrame.to_csv"""
        kwargs["index"] = False
        pd.DataFrame([i.to_dict() for i in subj]).to_csv(fp, **kwargs)
        logging.info(f"Successfully saved data to {fp}")


class ExcelFileAdapter(Adapter):

    obj_key = ".xlsx"
    alias = (".xlsx", "excel_file", "excel", "xlsx", "xls", ".xls")

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: str | Path, /, **kwargs
    ) -> list[dict]:
        return pd.read_excel(obj, **kwargs).to_dict(orient="records")

    @classmethod
    def to_obj(cls, subj: list[T], /, fp: str | Path, **kwargs) -> None:
        kwargs["index"] = False
        pd.DataFrame([i.to_dict() for i in subj]).to_excel(fp, **kwargs)
        logging.info(f"Saved {subj.class_name()} to {fp}")


NODE_ADAPTERS = [
    JsonAdapter,
    JsonFileAdapter,
    PandasSeriesAdapter,
]


class NodeAdapterRegistry(AdapterRegistry):
    _adapters = {k.obj_key: k() for k in NODE_ADAPTERS}


PILE_ADAPTERS = [
    JsonAdapter,
    JsonFileAdapter,
    PandasDataFrameAdapter,
    CSVFileAdapter,
    ExcelFileAdapter,
]


class PileAdapterRegistry(AdapterRegistry):

    _adapters = {k.obj_key: k() for k in PILE_ADAPTERS}
