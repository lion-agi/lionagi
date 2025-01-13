# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

# adapters/pandas_adapter.py
from typing import Any, TypeVar

import pandas as pd

from .base import Adapter

T = TypeVar("T")


class PandasDataFrameAdapter(Adapter[T]):
    """
    Adapts from a pandas DataFrame to a list of dicts (and back).
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        'obj' is expected to be a pandas DataFrame. We'll turn it into list[dict].
        """
        if not isinstance(obj, pd.DataFrame):
            raise ValueError(
                "PandasDataFrameAdapter.from_obj requires a pandas DataFrame as obj."
            )
        return obj.to_dict(orient="records")

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> pd.DataFrame:
        """
        Convert list of dicts to a DataFrame and return it (in-memory).
        """
        return pd.DataFrame(subj)
