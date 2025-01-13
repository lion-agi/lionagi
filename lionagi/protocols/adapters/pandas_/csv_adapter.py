import logging
from pathlib import Path

import pandas as pd

from lionagi.protocols._concepts import Collective

from ..adapter import Adapter, T


class CSVFileAdapter(Adapter):
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
        """kwargs for pd.read_csv"""
        df: pd.DataFrame = pd.read_csv(obj, **kwargs)
        dicts_ = df.to_dict(orient="records")
        return dicts_[0] if not many else dicts_

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        *,
        fp: str | Path,
        many: bool = False,
        **kwargs,
    ):
        """kwargs for pd.DataFrame.to_csv"""
        kwargs["index"] = False
        if many:
            if isinstance(subj, Collective):
                pd.DataFrame([i.to_dict() for i in subj]).to_csv(fp, **kwargs)
                logging.info(f"Successfully saved data to {fp}")
                return
            pd.DataFrame([subj.to_dict()]).to_csv(fp, **kwargs)
            logging.info(f"Successfully saved data to {fp}")
            return
        pd.DataFrame([subj.to_dict()]).to_csv(fp, **kwargs)
        logging.info(f"Successfully saved data to {fp}")
