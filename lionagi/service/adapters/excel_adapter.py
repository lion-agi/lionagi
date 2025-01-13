# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

# adapters/excel_adapter.py
from typing import Any, TypeVar

import pandas as pd

from .base import Adapter

T = TypeVar("T")


class ExcelFileAdapter(Adapter[T]):
    """
    Loads data from an Excel file into a list of dicts,
    and writes a list of dicts back to an Excel file (using pandas).
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        'obj' expected to be a file path (.xlsx).
        We use pandas.read_excel to get a DataFrame, then convert to list of dicts.
        """
        file_path = str(obj)
        sheet_name = kwargs.get("sheet_name", 0)  # default first sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df.to_dict(orient="records")

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Write data to an .xlsx file.
        Must have 'fp' in kwargs to specify file path.
        """
        file_path = kwargs.get("fp", None)
        if not file_path:
            raise ValueError(
                "ExcelFileAdapter.to_obj requires 'fp' (file path) in kwargs."
            )

        df = pd.DataFrame(subj)
        df.to_excel(file_path, index=False)
        return file_path
