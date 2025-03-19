"""
Defines a `PandasDataFrameAdapter` that converts between
a DataFrame and a list of dictionary-based elements.
"""

from datetime import datetime

import pandas as pd

from ..adapter import Adapter, T


class PandasDataFrameAdapter(Adapter):
    """
    Converts a set of objects to a single `pd.DataFrame`, or
    a DataFrame to a list of dictionaries. Typically used in memory,
    not for saving to file.
    """

    obj_key = "pd_dataframe"
    alias = ("pandas_dataframe", "pd.DataFrame", "pd_dataframe")

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: pd.DataFrame, /, **kwargs
    ) -> list[dict]:
        """
        Convert an existing DataFrame into a list of dicts.

        Parameters
        ----------
        subj_cls : type[T]
            The internal class to which we might parse.
        obj : pd.DataFrame
            The DataFrame to convert.
        **kwargs
            Additional args for DataFrame.to_dict (like `orient`).

        Returns
        -------
        list[dict]
            Each row as a dictionary.
        """
        return obj.to_dict(orient="records", **kwargs)

    @classmethod
    def to_obj(cls, subj: list[T], /, **kwargs) -> pd.DataFrame:
        """
        Convert multiple items into a DataFrame, adjusting `created_at` to datetime.

        Parameters
        ----------
        subj : list[T]
            The items to convert. Each item must have `to_dict()`.
        **kwargs
            Additional arguments for `pd.DataFrame(...)`.

        Returns
        -------
        pd.DataFrame
            The resulting DataFrame.
        """
        out_ = []
        for i in subj:
            _dict = i.to_dict()
            # Attempt to parse timestamps
            if "created_at" in _dict:
                try:
                    _dict["created_at"] = datetime.fromtimestamp(
                        _dict["created_at"]
                    )
                except Exception:
                    pass
            out_.append(_dict)
        df = pd.DataFrame(out_, **kwargs)
        # Convert created_at to datetime if present
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(
                df["created_at"], errors="coerce"
            )
        return df
