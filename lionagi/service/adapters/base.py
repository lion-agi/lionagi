# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

# adapters/base.py
from typing import Any, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class Adapter(Protocol[T]):
    """
    The base protocol for all adapters.
    Each adapter can handle 'from_obj' (loading data) and 'to_obj' (saving data),
    typically using different I/O formats: JSON strings, CSV file paths, DataFrames, etc.
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        Convert data from a given 'obj' into a list of dictionaries (the universal format).

        Args:
            subj_cls (type[T]):
                The domain type or class we intend to produce or parse into.
            obj (Any):
                The source data (could be a file path, a string, a DataFrame, etc.).
            **kwargs:
                Additional options (e.g. 'encoding', 'separator', etc.).

        Returns:
            A list of dictionaries representing the data in a uniform structure.

        Note:
            We often return 'list[dict]' for uniformity,
            even if it's a single record (like `[{"foo": "bar"}]`).
        """
        ...

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Takes a list of dictionaries (the universal format) and saves/returns
        them in the adapter's specialized format.

        Args:
            subj (list[dict]):
                A list of dictionary objects representing the data to save/serialize.
            **kwargs:
                Additional parameters for the output (like file path, compression, etc.).

        Returns:
            The converted data. Depending on the adapter, this might be a string,
            a file path, a DataFrame, or even None if it writes directly to disk.
        """
        ...
