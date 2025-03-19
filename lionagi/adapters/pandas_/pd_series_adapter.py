"""
Defines a `PandasSeriesAdapter` that converts a single object
to/from a `pd.Series`.
"""

import pandas as pd

from ..adapter import Adapter, T


class PandasSeriesAdapter(Adapter):
    """
    Converts a single item to a Pandas Series and vice versa.
    Great for 1-row data or simpler key-value pairs.
    """

    obj_key = "pd_series"
    alias = ("pandas_series", "pd.series", "pd_series")

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: pd.Series, /, **kwargs) -> dict:
        """
        Convert a Pandas Series into a dictionary.

        Parameters
        ----------
        subj_cls : type[T]
            Possibly the class we might use to rehydrate the item.
        obj : pd.Series
            The series to interpret.
        **kwargs
            Additional arguments for `Series.to_dict`.

        Returns
        -------
        dict
            The data from the Series as a dictionary.
        """
        return obj.to_dict(**kwargs)

    @classmethod
    def to_obj(cls, subj: T, /, **kwargs) -> pd.Series:
        """
        Convert a single item to a Series.

        Parameters
        ----------
        subj : T
            The item, which must have `to_dict()`.
        **kwargs
            Extra args passed to `pd.Series`.

        Returns
        -------
        pd.Series
        """
        return pd.Series(subj.to_dict(), **kwargs)
