import logging
from pathlib import Path

import pandas as pd

from lionagi.protocols._concepts import Collective

from ..adapter import Adapter, T


class CSVFileAdapter(Adapter):
    """
    Reads/writes CSV files to a list of dicts or vice versa,
    using `pandas`.
    """

    obj_key = ".csv"

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
        Read a CSV file into a list of dictionaries.

        Parameters
        ----------
        subj_cls : type[T]
            The target class for context (not used).
        obj : str | Path
            The CSV file path.
        many : bool, optional
            If True, returns list[dict]; if False, returns only
            the first dict.
        **kwargs
            Additional options for `pd.read_csv`.

        Returns
        -------
        list[dict]
            The parsed CSV data as a list of row dictionaries.
        """
        df: pd.DataFrame = pd.read_csv(obj, **kwargs)
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
        Write an object's data to a CSV file.

        Parameters
        ----------
        subj : T
            The item(s) to convert. If `many=True`, can be a Collective.
        fp : str | Path
            File path to write the CSV.
        many : bool
            If True, we assume a collection of items, else a single item.
        **kwargs
            Extra params for `DataFrame.to_csv`.

        Returns
        -------
        None
        """
        kwargs["index"] = False  # By default, do not save index
        if many:
            if isinstance(subj, Collective):
                pd.DataFrame([i.to_dict() for i in subj]).to_csv(fp, **kwargs)
            else:
                pd.DataFrame([subj.to_dict()]).to_csv(fp, **kwargs)
        else:
            pd.DataFrame([subj.to_dict()]).to_csv(fp, **kwargs)
        logging.info(f"CSV data saved to {fp}")


# File: lionagi/protocols/adapters/pandas_/csv_adapter.py
