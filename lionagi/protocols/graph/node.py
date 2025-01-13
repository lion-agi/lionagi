# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any, ClassVar

from pydantic import field_validator

from lionagi._class_registry import LION_CLASS_REGISTRY

from .._concepts import Relational
from ..adapters.adapter import AdapterRegistry
from ..adapters.json_adapter import JsonAdapter, JsonFileAdapter
from ..adapters.pandas_.pd_series_adapter import PandasSeriesAdapter
from ..generic.element import Element

NODE_DEFAULT_ADAPTERS = (
    JsonAdapter,
    JsonFileAdapter,
    PandasSeriesAdapter,
)


class NodeAdapterRegistry(AdapterRegistry):
    pass


for i in NODE_DEFAULT_ADAPTERS:
    NodeAdapterRegistry.register(i)

__all__ = ("Node",)


class Node(Element, Relational):
    """
    A base class for all Nodes in a graph, storing:
      - Arbitrary content
      - Metadata as a dict
      - An optional numeric embedding (list of floats)
      - Automatic subclass registration
    """

    _adapter_registry: ClassVar[AdapterRegistry] = NodeAdapterRegistry

    content: Any = None
    embedding: list[float] | None = None

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize and register subclasses in the global class registry."""
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.class_name(full=True)] = cls

    @field_validator("embedding", mode="before")
    def _parse_embedding(
        cls, value: list[float] | str | None
    ) -> list[float] | None:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                loaded = json.loads(value)
                if not isinstance(loaded, list):
                    raise ValueError
                return [float(x) for x in loaded]
            except Exception as e:
                raise ValueError("Invalid embedding string.") from e
        if isinstance(value, list):
            try:
                return [float(x) for x in value]
            except Exception as e:
                raise ValueError("Invalid embedding list.") from e
        raise ValueError(
            "Invalid embedding type; must be list or JSON-encoded string."
        )

    def adapt_to(
        self, obj_key: str, /, many: bool = False, **kwargs: Any
    ) -> Any:
        """
        Convert this Node to another format using a registered adapter.
        """
        return self._get_adapter_registry().adapt_to(
            self, obj_key, many=many, **kwargs
        )

    @classmethod
    def adapt_from(
        cls,
        obj: Any,
        obj_key: str,
        /,
        many: bool = False,
        **kwargs: Any,
    ) -> "Node":
        """
        Construct a Node from an external format using a registered adapter.
        If the adapter returns a dictionary with 'lion_class', we can
        auto-delegate to the correct subclass via from_dict.
        """
        result = cls._get_adapter_registry().adapt_from(
            cls, obj, obj_key, many=many, **kwargs
        )
        # If adapter returned multiple items, choose the first or handle as needed.
        if isinstance(result, list):
            result = result[0]
        return cls.from_dict(result)

    @classmethod
    def _get_adapter_registry(cls) -> AdapterRegistry:
        if isinstance(cls._adapter_registry, type):
            cls._adapter_registry = cls._adapter_registry()
        return cls._adapter_registry

    @classmethod
    def register_adapter(cls, adapter: Any) -> None:
        cls._get_adapter_registry().register(adapter)

    @classmethod
    def list_adapters(cls) -> list[str]:
        return cls._get_adapter_registry().list_adapters()


# File: protocols/graph/node.py
