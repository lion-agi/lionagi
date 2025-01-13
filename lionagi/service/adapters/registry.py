# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

# adapters/registry.py
from typing import Any, TypeVar

from .base import Adapter

T = TypeVar("T")


class AdapterRegistry:
    """
    A registry holding references to multiple adapters, keyed by strings.
    E.g. ".json" -> JsonFileAdapter, "csv" -> CSVFileAdapter, "pd_dataframe" -> PandasDataFrameAdapter
    """

    def __init__(self):
        self._registry: dict[str, type[Adapter]] = {}

    def register(self, key: str, adapter_cls: type[Adapter[T]]) -> None:
        """
        Register an adapter class under a certain key string.

        Args:
            key (str): The identifier, e.g. ".json", "csv", "pd_dataframe", etc.
            adapter_cls (Type[Adapter[T]]): The adapter class to register.
        """
        self._registry[key] = adapter_cls

    def get(self, key: str) -> type[Adapter[T]]:
        """
        Retrieve the adapter class for the given key.

        Raises:
            KeyError: If no adapter is registered under that key.
        """
        if key not in self._registry:
            raise KeyError(f"No adapter registered for key: {key}")
        return self._registry[key]

    def adapt_from(
        self, subj_cls: type[T], obj: Any, key: str, **kwargs
    ) -> list[dict]:
        """
        Convenience method to directly convert data from 'obj' using the adapter registered under 'key'.
        """
        adapter_cls = self.get(key)
        return adapter_cls.from_obj(subj_cls, obj, **kwargs)

    def adapt_to(self, subj: list[dict], key: str, **kwargs) -> Any:
        """
        Convenience method to convert 'subj' (a list of dicts) to the format handled by the adapter under 'key'.
        """
        adapter_cls = self.get(key)
        return adapter_cls.to_obj(subj, **kwargs)
