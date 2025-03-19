"""
Provides an ExcelFileAdapter for reading/writing Excel (.xlsx) files
via pandas.
"""

import logging
from pathlib import Path

import pandas as pd

from lionagi.protocols._concepts import Collective

from ..adapter import Adapter, T


class ExcelFileAdapter(Adapter):
    """
    Reads/writes Excel (XLSX) files, using `pandas`.
    """

    obj_key = ".xlsx"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: str | Path,
        /,
        *,
        many: bool = False,
        **kwargs,
    ) -> list[dict]:
        """
        Read an Excel file into a list of dictionaries.

        Parameters
        ----------
        subj_cls : type[T]
            Target class for context.
        obj : str | Path
            The Excel file path.
        many : bool, optional
            If True, returns list[dict]. If False, returns single dict or first element.
        **kwargs
            Additional options for `pd.read_excel`.

        Returns
        -------
        list[dict]
        """
        df: pd.DataFrame = pd.read_excel(obj, **kwargs)
        dicts_ = df.to_dict(orient="records")
        if many:
            return dicts_
        return dicts_[0] if len(dicts_) > 0 else {}

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        *,
        fp: str | Path,
        many: bool = False,
        **kwargs,
    ) -> None:
        """
        Write data to an Excel file.

        Parameters
        ----------
        subj : T
            The object(s) to convert to Excel rows.
        fp : str | Path
            Path to save the XLSX file.
        many : bool
            If True, writes multiple items (e.g., a Collective).
        **kwargs
            Extra parameters for `DataFrame.to_excel`.
        """
        kwargs["index"] = False
        if many:
            if isinstance(subj, Collective):
                pd.DataFrame([i.to_dict() for i in subj]).to_excel(
                    fp, **kwargs
                )
            else:
                pd.DataFrame([subj.to_dict()]).to_excel(fp, **kwargs)
        else:
            pd.DataFrame([subj.to_dict()]).to_excel(fp, **kwargs)
        logging.info(f"Excel data saved to {fp}")


# File: lionagi/protocols/adapters/pandas_/excel_adapter.py
