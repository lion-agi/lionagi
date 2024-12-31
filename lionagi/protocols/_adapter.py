# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from abc import ABC
from collections.abc import Iterable
from pathlib import Path
from typing import Any, ClassVar, Protocol, runtime_checkable

import pandas as pd
from typing_extensions import get_protocol_members

from .generic.element import E

__all__ = (
    "Adapter",
    "AdapterRegistry",
    "JsonAdapter",
    "JsonFileAdapter",
    "PandasSeriesAdapter",
    "PandasDataFrameAdapter",
    "CSVFileAdapter",
    "ExcelFileAdapter",
    "Adaptable",
    "DEFAULT_ADAPTERS",
)


@runtime_checkable
class Adapter(Protocol):

    obj_key: ClassVar[str]
    alias: ClassVar[tuple[str, ...]] = ()

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[E],
        obj: Any | list[Any],
        *,
        many: bool = False,
        **kwargs,
    ) -> dict | list[dict]: ...

    @classmethod
    def to_obj(
        cls,
        subj: E,
        *,
        many: bool = False,
        **kwargs,
    ) -> Any: ...


ADAPTER_MEMBERS = get_protocol_members(Adapter)  # duck typing


class AdapterRegistry:

    _adapters: dict[str, Adapter | str] = {}

    @classmethod
    def list_adapters(cls) -> list[tuple[str | type, ...]]:
        return list(cls._adapters.keys())

    @classmethod
    def register(cls, adapter: type[Adapter]) -> None:
        for member in ADAPTER_MEMBERS:
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

        for i in adapter.alias:
            if i in cls._adapters:
                raise ValueError(f"Adapter alias {i} already in use.")
            else:
                cls._adapters[i] = adapter.obj_key

    @classmethod
    def get(cls, obj_key: type | str, /) -> Adapter:
        try:
            a = cls._adapters[obj_key]
            if isinstance(a, str):
                return cls._adapters[cls._adapters[a]]
            return a
        except Exception as e:
            logging.error(f"Error getting adapter for {obj_key}. Error: {e}")
            raise e

    @classmethod
    def adapt_from(
        cls,
        subj_cls: type[E],
        obj: Any,
        obj_key: type | str,
        *,
        many: bool = False,
        **kwargs,
    ) -> dict | list[dict]:
        try:
            return cls.get(obj_key).from_obj(
                subj_cls, obj, many=many, **kwargs
            )
        except Exception as e:
            logging.error(f"Error adapting data from {obj_key}. Error: {e}")
            raise e

    @classmethod
    def adapt_to(
        cls,
        subj: E,
        obj_key: type | str,
        *,
        many: bool = False,
        **kwargs,
    ) -> Any:
        try:
            return cls.get(obj_key).to_obj(subj, many=many, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data to {obj_key}. Error: {e}")
            raise e


class JsonAdapter(Adapter):

    obj_key = "json"
    alias = ("json_str", "json_string")

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[E],
        obj: str | list[str],
        *,
        many: bool = False,
        **kwargs,
    ) -> dict | list[dict]:
        """
        kwargs for json.loads
        """
        return json.loads(obj, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subj: E | Iterable[E],
        *,
        many: bool = False,
        **kwargs,
    ) -> str | list[str]:
        if many:
            return [json.dumps(i.to_dict(), **kwargs) for i in subj]
        return json.dumps(subj.to_dict())


class JsonFileAdapter(Adapter):

    obj_key = ".json"
    obj_key = (".json", "json_file", "jsonl_file", ".jsonl")

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[E],
        obj: str | Path,
        *,
        many: bool = False,
        **kwargs,
    ) -> dict:
        """kwargs for json.load"""
        with open(obj) as f:
            return json.load(f, **kwargs)

    @classmethod
    def to_obj(
        cls,
        subj: E | Iterable[E],
        *,
        many: bool = False,
        serialization_kwargs: dict = {},
        fp: str | Path,
        **kwargs,
    ) -> None:
        """kwargs for json.dump"""
        data = (
            [i.to_dict(**serialization_kwargs) for i in subj]
            if many
            else subj.to_dict(**serialization_kwargs)
        )

        with open(fp, "w") as f:
            json.dump(data, f, **kwargs)


class PandasSeriesAdapter(Adapter):

    obj_key = "pd_series"
    alias = ("pandas_series", "pd.series")

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[E],
        obj: pd.Series | list[pd.Series],
        *,
        many: bool = False,
        **kwargs,
    ) -> dict | list[dict]:
        if many:
            obj = obj if isinstance(obj, list) else [obj]
            return [i.to_dict() for i in obj]
        return obj.to_dict()

    @classmethod
    def to_obj(
        cls,
        subj: E | list[E],
        /,
        many: bool = False,
        **kwargs,
    ) -> pd.Series | list[pd.Series]:
        if many:
            return [pd.Series(i.to_dict(), **kwargs) for i in subj]
        return pd.Series(subj.to_dict(), **kwargs)


class PandasDataFrameAdapter(Adapter):

    obj_key = "pd_dataframe"
    alias = ("pandas_dataframe", "pd.DataFrame")

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[E],
        obj: pd.DataFrame,
        /,
        many: bool = False,
        **kwargs,
    ) -> list[dict]:
        """kwargs for pd.DataFrame.to_dict"""
        if many:
            return obj.to_dict(orient="records", **kwargs)
        return obj.to_dict(orient="records", **kwargs)[0]

    @classmethod
    def to_obj(
        cls, subj: list[E], /, many: bool = False, **kwargs
    ) -> pd.DataFrame:
        """kwargs for pd.DataFrame"""
        subj = [subj] if isinstance(subj, E) else list(subj)
        out_ = []
        for i in subj:
            _dict = i.to_dict()
            _dict["timestamp"] = i.created_at
            out_.append(_dict)
        df = pd.DataFrame(out_, **kwargs)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df


class CSVFileAdapter(Adapter):

    obj_key = ".csv"
    alias = ("csv_file", "csv")

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[E],
        obj: str | Path,
        /,
        many: bool = False,
        **kwargs,
    ) -> list[dict]:
        """kwargs for pd.read_csv"""
        df: pd.DataFrame = pd.read_csv(obj, **kwargs)
        if many:
            df.to_dict(orient="records")
        else:
            return df.to_dict(orient="records")[0]

    @classmethod
    def to_obj(
        cls,
        subj: E | list[E],
        *,
        many: bool = False,
        fp: str | Path,
        serialization_kwargs: dict = {},
        **kwargs,
    ) -> None:
        """kwargs for pd.DataFrame.to_csv"""
        kwargs["index"] = False
        subj = [subj] if isinstance(subj, E) else list(subj)

        pd.DataFrame([i.to_dict(**serialization_kwargs) for i in subj]).to_csv(
            fp, **kwargs
        )
        logging.info(f"Successfully saved data to {fp}")


class ExcelFileAdapter(Adapter):

    obj_key = ".xlsx"
    alias = ("excel_file", "excel", "xlsx", "xls", ".xls")

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[E],
        obj: str | Path,
        /,
        many: bool = False,
        **kwargs,
    ) -> list[dict]:
        if not many:
            return pd.read_excel(obj, **kwargs).to_dict(orient="records")[0]
        return pd.read_excel(obj, **kwargs).to_dict(orient="records")

    @classmethod
    def to_obj(
        cls, subj: E | list[E], /, fp: str | Path, many: bool = False, **kwargs
    ) -> None:
        kwargs["index"] = False
        subj = [subj] if isinstance(subj, E) else list(subj)
        pd.DataFrame([i.to_dict() for i in subj]).to_excel(fp, **kwargs)
        logging.info(f"Saved {subj.class_name()} to {fp}")


class Adaptable(ABC):

    adapter_registry: ClassVar[AdapterRegistry]

    def adapt_to(
        self, obj_key: str, /, many: bool = False, **kwargs: Any
    ) -> Any:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> "Adaptable":
        raise NotImplementedError

    @classmethod
    def adapt_from(cls, obj: Any, obj_key: str, /, many: bool, **kwargs: Any):
        raise NotImplementedError

    @classmethod
    def list_adapters(cls):
        """List all registered adapters for this component type.

        Returns:
            list: Available adapters for this component type.
        """
        return cls._get_adapter_registry().list_adapters()

    @classmethod
    def register_adapter(cls, adapter: type[Adapter]):
        """Register a new adapter for this component type.

        Args:
            adapter: The adapter class to register.
        """
        cls._get_adapter_registry().register(adapter)

    @classmethod
    def _get_adapter_registry(cls) -> AdapterRegistry:
        """Get the converter registry for the class."""
        if isinstance(cls._adapter_registry, type):
            cls._adapter_registry = cls._adapter_registry()
        return cls._adapter_registry


DEFAULT_ADAPTERS = (
    JsonAdapter,
    JsonFileAdapter,
    PandasSeriesAdapter,
    PandasDataFrameAdapter,
    CSVFileAdapter,
    ExcelFileAdapter,
)
