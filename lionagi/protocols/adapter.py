# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Adapter registry system for managing data format conversions and I/O operations.
Supports JSON, CSV, Pandas Series/DataFrame, and file handling with extensible adapter pattern.
"""

import json
import logging
from pathlib import Path
from typing import Any, Protocol, TypeVar, runtime_checkable

import pandas as pd
from typing_extensions import get_protocol_members

T = TypeVar("T")


@runtime_checkable
class Adapter(Protocol):
    """Protocol defining the interface for data format adapters."""

    obj_key: str

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: Any, /, many=False, **kwargs
    ) -> dict | list[dict]: ...

    @classmethod
    def to_obj(cls, subj: T, /, many=False, **kwargs) -> Any: ...


adapter_members = get_protocol_members(Adapter)  # duck typing


class AdapterRegistry:
    """Registry for managing and accessing data format adapters."""

    _adapters: dict[str, Adapter] = {}

    @classmethod
    def list_adapters(cls) -> list[tuple[str | type, ...]]:
        """Returns list of registered adapter keys."""
        return list(cls._adapters.keys())

    @classmethod
    def register(cls, adapter: type[Adapter]) -> None:
        """Registers a new adapter after validating its interface."""
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
        """Retrieves registered adapter by key."""
        try:
            return cls._adapters[obj_key]
        except Exception as e:
            logging.error(f"Error getting adapter for {obj_key}. Error: {e}")

    @classmethod
    def adapt_from(
        cls, subj_cls: type[T], obj: Any, obj_key: type | str, **kwargs
    ) -> dict | list[dict]:
        """Converts input data to dictionary format using specified adapter."""
        try:
            return cls.get(obj_key).from_obj(subj_cls, obj, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data from {obj_key}. Error: {e}")
            raise e

    @classmethod
    def adapt_to(cls, subj: T, obj_key: type | str, **kwargs) -> Any:
        """Converts data to target format using specified adapter."""
        try:
            return cls.get(obj_key).to_obj(subj, **kwargs)
        except Exception as e:
            logging.error(f"Error adapting data to {obj_key}. Error: {e}")
            raise e


class JsonAdapter(Adapter):
    """Adapter for JSON string conversion."""

    obj_key = "json"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: str | list,
        /,
        many=False,
    ) -> dict:
        """Converts JSON string to dictionary."""
        if many:
            obj = [obj] if not isinstance(obj, list) else obj
            return [json.loads(i) for i in obj]

        return json.loads(obj)

    @classmethod
    def to_obj(cls, subj: T, many=False) -> str:
        """Converts object to JSON string."""
        if many:
            return [json.dumps(i.to_dict()) for i in subj]
        return json.dumps(subj.to_dict())


class JsonFileAdapter(Adapter):
    """Adapter for JSON file I/O operations."""

    obj_key = ".json"

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: str | Path, /, many=False
    ) -> dict:
        """Loads dictionary from JSON file."""
        with open(obj) as f:
            return json.load(f)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        fp: str | Path,
        many=False,
    ) -> None:
        """Saves object to JSON file."""
        if many:
            with open(fp, "a") as f:
                json.dump([i.to_dict() for i in subj], f)
        else:
            with open(fp, "w") as f:
                json.dump(subj.to_dict(), f)
        logging.info(f"Successfully saved data to {fp}")


class PandasSeriesAdapter(Adapter):
    """Adapter for Pandas Series conversion."""

    obj_key = "pd_series"

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: pd.Series, /, many=False, **kwargs
    ) -> dict:
        """Converts Pandas Series to dictionary."""
        if many:
            obj = [obj] if not isinstance(obj, list) else obj
            return [i.to_dict(**kwargs) for i in obj]
        return obj.to_dict(**kwargs)

    @classmethod
    def to_obj(cls, subj: T, /, many=False, **kwargs) -> pd.Series:
        """Converts object to Pandas Series."""
        if many:
            subj = [subj] if not isinstance(subj, list) else subj
            return [pd.Series(i.to_dict(), **kwargs) for i in subj]
        return pd.Series(subj.to_dict(), **kwargs)


class PandasDataFrameAdapter(Adapter):
    """Adapter for Pandas DataFrame conversion."""

    obj_key = "pd_dataframe"

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: pd.DataFrame, /, many=False, **kwargs
    ) -> list[dict]:
        """Converts DataFrame to list of dictionaries."""
        lst_ = obj.to_dict(orient="records", **kwargs)
        if not many:
            return lst_[0]
        return lst_

    @classmethod
    def to_obj(cls, subj: list[T], /, many=False, **kwargs) -> pd.DataFrame:
        """Converts list of objects to DataFrame."""
        out_ = []
        subj = [subj] if not isinstance(subj, list) else subj
        for i in subj:
            _dict = i.to_dict()
            _dict["timestamp"] = i.created_datetime
            out_.append(_dict)
        df = pd.DataFrame(out_, **kwargs)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df


class CSVFileAdapter(Adapter):
    """Adapter for CSV file I/O operations."""

    obj_key = ".csv"

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: str | Path, /, many=False, **kwargs
    ) -> list[dict]:
        """Loads list of dictionaries from CSV file."""
        df: pd.DataFrame = pd.read_csv(obj, **kwargs)
        if not many:
            return df.to_dict(orient="records")[0]
        return df.to_dict(orient="records")

    @classmethod
    def to_obj(
        cls,
        subj: list[T],
        /,
        fp: str | Path,
        many=False,
        **kwargs,
    ) -> None:
        """Saves list of objects to CSV file."""
        subj = [subj] if not isinstance(subj, list) else subj
        pd.DataFrame([i.to_dict() for i in subj]).to_csv(fp, **kwargs)
        logging.info(f"Successfully saved data to {fp}")


class ComponentRegistry(AdapterRegistry):
    """Registry for component-specific adapters."""


class PileRegistry(AdapterRegistry):
    """Registry for pile-specific adapters."""


ADAPTERS = {
    JsonAdapter,
    JsonFileAdapter,
    PandasSeriesAdapter,
    PandasDataFrameAdapter,
    CSVFileAdapter,
}


for i in ADAPTERS:
    ComponentRegistry.register(i)
    PileRegistry.register(i)


# File: lionagi/protocols/adapter.py
