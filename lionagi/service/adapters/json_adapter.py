# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

# adapters/json_adapter.py
import json
from typing import Any, TypeVar

from .base import Adapter

T = TypeVar("T")


class JsonAdapter(Adapter[T]):
    """
    Adapts data from a JSON string to a list of dicts, and back to a JSON string.
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        If 'obj' is a string (JSON text), parse it.
        If 'obj' is already a dict/list, just transform it as needed.
        """
        if isinstance(obj, str):
            # assume it's a JSON string
            data = json.loads(obj)
        else:
            # might already be Python objects
            data = obj

        # Ensure it's a list of dicts
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            # If the list doesn't contain dicts, you may transform them, but let's assume they are dicts
            return data
        else:
            raise ValueError(
                "JSONAdapter can only parse a dict or list of dicts from JSON"
            )

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> str:
        """
        Convert the list of dicts into a JSON string.
        Allows passing 'indent' or 'sort_keys' as kwargs for custom formatting.
        """
        return json.dumps(subj, **kwargs)


class JsonFileAdapter(Adapter[T]):
    """
    Loads data from a .json file path, and saves back to a .json file.
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        'obj' is expected to be a file path (str or Path) pointing to a .json file.
        """
        filepath = str(obj)
        with open(filepath, encoding=kwargs.get("encoding", "utf-8")) as f:
            data = json.load(f)

        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("JSON file must contain a dict or list of dicts")

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Write data to the specified file path if provided in kwargs.
        Returns the file path for convenience, or raises ValueError if missing.
        """
        file_path = kwargs.get("fp", None)
        if not file_path:
            raise ValueError(
                "JsonFileAdapter.to_obj requires 'fp' (file path) in kwargs."
            )

        with open(
            file_path, "w", encoding=kwargs.get("encoding", "utf-8")
        ) as f:
            json.dump(subj, f, indent=kwargs.get("indent", 2))
        return file_path
