# adapters/csv_adapter.py
import csv
from typing import Any, Dict, List, TypeVar

from .base import Adapter

T = TypeVar("T")


class CSVFileAdapter(Adapter[T]):
    """
    Loads a CSV file into a list of dicts (using the first row as headers).
    Saves a list of dicts back into a CSV file.
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        'obj' is expected to be a file path. We open and read it with Python's csv DictReader.
        """
        path = str(obj)
        encoding = kwargs.get("encoding", "utf-8")
        delimiter = kwargs.get("delimiter", ",")
        data = []
        with open(path, encoding=encoding, newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                data.append(dict(row))
        return data

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Writes 'subj' (list of dicts) to a CSV file.
        Expects 'fp' in kwargs as the output file path.
        """
        file_path = kwargs.get("fp", None)
        if not file_path:
            raise ValueError(
                "CSVFileAdapter.to_obj requires 'fp' parameter in kwargs."
            )

        if not subj:
            # If there's no data, we can't infer headers
            with open(
                file_path,
                mode="w",
                encoding=kwargs.get("encoding", "utf-8"),
                newline="",
            ) as f:
                # just create an empty file
                pass
            return file_path

        # Otherwise, gather column headers from the first row
        fieldnames = list(subj[0].keys())

        encoding = kwargs.get("encoding", "utf-8")
        delimiter = kwargs.get("delimiter", ",")
        with open(file_path, mode="w", encoding=encoding, newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=fieldnames, delimiter=delimiter
            )
            writer.writeheader()
            for row in subj:
                writer.writerow(row)

        return file_path
