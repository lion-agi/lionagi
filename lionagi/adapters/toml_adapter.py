"""
Implements two adapters:
- `TomlAdapter` for in-memory TOML strings
- `TomlFileAdapter` for reading/writing TOML files
"""

import logging
from pathlib import Path

import toml

from lionagi.protocols._concepts import Collective

from .adapter import Adapter, T


class TomlAdapter(Adapter):
    """
    Adapter that converts to/from TOML **strings** in memory.
    Example usage: taking a Python dictionary and making TOML,
    or parsing TOML string to a dict.
    """

    obj_key = "toml"

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
        Convert a TOML string into a dict or list of dicts.

        Parameters
        ----------
        subj_cls : type[T]
            The target class for context (not always used).
        obj : str
            The TOML string.
        many : bool, optional
            If True, expects a TOML array of tables (returns list[dict]).
            Otherwise returns a single dict.
        **kwargs
            Extra arguments for toml.loads().

        Returns
        -------
        dict | list[dict]
            The loaded TOML data.
        """
        result = toml.loads(obj, **kwargs)

        # Handle array of tables in TOML for "many" case
        if many:
            # Check if there's a top-level array key that might hold multiple items
            for key, value in result.items():
                if isinstance(value, list) and all(
                    isinstance(item, dict) for item in value
                ):
                    return value
            # If no array of tables found, wrap the result in a list
            return [result]

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
        Convert an object (or collection) to a TOML string.

        Parameters
        ----------
        subj : T
            The object to serialize.
        many : bool, optional
            If True, convert multiple items to a TOML array of tables.
        **kwargs
            Extra arguments for toml.dumps().

        Returns
        -------
        str
            The resulting TOML string.
        """
        if many:
            if isinstance(subj, Collective):
                # For multiple items, create a wrapper dict with an array of items
                data = {"items": [i.to_dict() for i in subj]}
            else:
                data = {"items": [subj.to_dict()]}
            return toml.dumps(data, **kwargs)

        return toml.dumps(subj.to_dict(), **kwargs)


class TomlFileAdapter(Adapter):
    """
    Adapter that reads/writes TOML data to/from a file on disk.
    The file extension key is ".toml".
    """

    obj_key = ".toml"

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
        Read a TOML file from disk and return a dict or list of dicts.

        Parameters
        ----------
        subj_cls : type[T]
            The target class for context.
        obj : str | Path
            The TOML file path.
        many : bool
            If True, expects an array of tables. Otherwise single dict.
        **kwargs
            Extra arguments for toml.load().

        Returns
        -------
        dict | list[dict]
            The loaded data from file.
        """
        with open(obj, "r", encoding="utf-8") as f:
            result = toml.load(f, **kwargs)

        # Handle array of tables in TOML for "many" case
        if many:
            # Check if there's a top-level array key that might hold multiple items
            for key, value in result.items():
                if isinstance(value, list) and all(
                    isinstance(item, dict) for item in value
                ):
                    return value
            # If no array of tables found, wrap the result in a list
            return [result]

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
        Write a dict (or list) to a TOML file.

        Parameters
        ----------
        subj : T
            The object/collection to serialize.
        fp : str | Path
            The file path to write.
        many : bool
            If True, write as a TOML array of tables of multiple items.
        mode : str
            File open mode, defaults to write ("w").
        **kwargs
            Extra arguments for toml.dump().

        Returns
        -------
        None
        """
        with open(fp, mode, encoding="utf-8") as f:
            if many:
                if isinstance(subj, Collective):
                    # TOML requires arrays of tables to be in a table
                    data = {"items": [i.to_dict() for i in subj]}
                else:
                    data = {"items": [subj.to_dict()]}
                toml.dump(data, f, **kwargs)
            else:
                toml.dump(subj.to_dict(), f, **kwargs)
        logging.info(f"TOML data saved to {fp}")


# File: lionagi/protocols/adapters/toml_adapter.py
