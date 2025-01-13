from datetime import datetime

import pandas as pd

from ..adapter import Adapter, T


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
