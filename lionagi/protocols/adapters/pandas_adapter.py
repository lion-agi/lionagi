# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from pathlib import Path

import pandas as pd

from lionagi.integrations.pandas_ import to_df
from lionagi.protocols.adapters.adapter import Adapter, T


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
            _dict["timestamp"] = i.created_datetime
            out_.append(_dict)
        df = to_df(out_, **kwargs)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
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
        to_df([i.to_dict() for i in subj]).to_csv(fp, **kwargs)
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
        to_df([i.to_dict() for i in subj]).to_excel(fp, **kwargs)
        logging.info(f"Saved {subj.class_name()} to {fp}")
