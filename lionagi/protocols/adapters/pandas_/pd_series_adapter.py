import pandas as pd

from ..adapter import Adapter, T


class PandasSeriesAdapter(Adapter):

    obj_key = "pd_series"
    alias = ("pandas_series", "pd.series", "pd_series")

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: pd.Series, /, **kwargs) -> dict:
        return obj.to_dict(**kwargs)

    @classmethod
    def to_obj(cls, subj: T, /, **kwargs) -> pd.Series:
        return pd.Series(subj.to_dict(), **kwargs)
