"""
Implements two adapters:
- `JsonAdapter` for in-memory JSON strings
- `JsonFileAdapter` for reading/writing JSON files
"""

import json
import logging
from pathlib import Path

from lionagi.protocols._concepts import Collective

from .adapter import Adapter, T


class JsonAdapter(Adapter):
    """
    Adapter that converts to/from JSON **strings** in memory.
    Example usage: taking a Python dictionary and making JSON,
    or parsing JSON string to a dict.
    """

    obj_key = "json"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: str,
        /,
        *,
        many: bool = False,
        **kwargs,
    ) -> dict | list[dict]:
        """
        Convert a JSON string into a dict or list of dicts.

        Parameters
        ----------
        subj_cls : type[T]
            The target class for context (not always used).
        obj : str
            The JSON string.
        many : bool, optional
            If True, expects a JSON array (returns list[dict]).
            Otherwise returns a single dict or the first element.
        **kwargs
            Extra arguments for json.loads().

        Returns
        -------
        dict | list[dict]
            The loaded JSON data.
        """
        result = json.loads(obj, **kwargs)
        if many:
            return result if isinstance(result, list) else [result]
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result

    @classmethod
    def to_obj(
        cls,
        subj: T,
        *,
        many: bool = False,
        **kwargs,
    ) -> str:
        """
        Convert an object (or collection) to a JSON string.

        Parameters
        ----------
        subj : T
            The object to serialize.
        many : bool, optional
            If True, convert multiple items to a JSON array.
        **kwargs
            Extra arguments for json.dumps().

        Returns
        -------
        str
            The resulting JSON string.
        """
        if many:
            if isinstance(subj, Collective):
                data = [i.to_dict() for i in subj]
            else:
                data = [subj.to_dict()]
            return json.dumps(data, **kwargs)
        return json.dumps(subj.to_dict(), **kwargs)


class JsonFileAdapter(Adapter):
    """
    Adapter that reads/writes JSON data to/from a file on disk.
    The file extension key is ".json".
    """

    obj_key = ".json"

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: str | Path,
        /,
        *,
        many: bool = False,
        **kwargs,
    ) -> dict | list[dict]:
        """
        Read a JSON file from disk and return a dict or list of dicts.

        Parameters
        ----------
        subj_cls : type[T]
            The target class for context.
        obj : str | Path
            The JSON file path.
        many : bool
            If True, expects a list. Otherwise single dict or first element.
        **kwargs
            Extra arguments for json.load().

        Returns
        -------
        dict | list[dict]
            The loaded data from file.
        """
        with open(obj, encoding="utf-8") as f:
            result = json.load(f, **kwargs)
        if many:
            return result if isinstance(result, list) else [result]
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        *,
        fp: str | Path,
        many: bool = False,
        mode: str = "w",
        **kwargs,
    ) -> None:
        """
        Write a dict (or list) to a JSON file.

        Parameters
        ----------
        subj : T
            The object/collection to serialize.
        fp : str | Path
            The file path to write.
        many : bool
            If True, write as a JSON array of multiple items.
        **kwargs
            Extra arguments for json.dump().

        Returns
        -------
        None
        """
        with open(fp, mode, encoding="utf-8") as f:
            if many:
                if isinstance(subj, Collective):
                    json.dump([i.to_dict() for i in subj], f, **kwargs)
                else:
                    json.dump([subj.to_dict()], f, **kwargs)
            else:
                json.dump(subj.to_dict(), f, **kwargs)
        logging.info(f"JSON data saved to {fp}")


# File: lionagi/protocols/adapters/json_adapter.py
