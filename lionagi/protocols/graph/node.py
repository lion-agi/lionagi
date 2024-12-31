# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from typing import Any, ClassVar

from lionagi._class_registry import LION_CLASS_REGISTRY, get_class

from .._adapter import DEFAULT_ADAPTERS, Adaptable, AdapterRegistry
from ..generic.concepts import Relational
from ..generic.element import Element

__all__ = ("Node",)


class NodeAdapterRegistry(AdapterRegistry):
    """Registry for Node-specific adapters."""


for adapter in DEFAULT_ADAPTERS:
    NodeAdapterRegistry.register(adapter)


class Node(Element, Adaptable, Relational):
    """
    A base class for all Nodes in a graph, storing:
      - Arbitrary content
      - Metadata as a dict
      - An optional numeric embedding (list of floats)
      - Automatic subclass registration
    """

    adapter_registry: ClassVar[AdapterRegistry] = NodeAdapterRegistry

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Called when a Node subclass is defined, automatically adding
        it to NODE_CLASS_REGISTRY under its class name.
        """
        super().__init_subclass__(**kwargs)
        cls_name = cls.__name__
        if cls_name not in LION_CLASS_REGISTRY:
            LION_CLASS_REGISTRY[cls_name] = cls

    def __init__(
        self,
        content: Any = None,
        metadata: dict | None = None,
        embedding: list[float] | str | None = None,
        **kwargs: Any,
    ):
        """
        Args:
            content:
                Arbitrary content for the node.
            metadata:
                A dictionary of metadata fields.
            embedding:
                A list of floats or a JSON-encoded string representing floats.
            **kwargs:
                Passed to Element.__init__ (e.g. `id`, `created_at`).
        """
        super().__init__(**kwargs)
        self.content = content
        self.metadata: dict = metadata if metadata is not None else {}
        self.embedding: list[float] | None = self._parse_embedding(embedding)

    def _parse_embedding(
        self, value: list[float] | str | None
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

    def to_dict(self) -> dict[str, Any]:
        dict_ = super().to_dict()
        dict_["content"] = self.content
        dict_["metadata"] = self.metadata
        dict_["embedding"] = self.embedding
        return dict_

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Node:
        """
        Deserialize a Node or subclass from a dictionary. If the dict
        contains a 'lion_class' key referencing a registered subclass,
        delegates creation to that subclass's from_dict.

        Args:
            data (dict): The dictionary representing a node.

        Returns:
            Node: An instance of Node or a registered subclass.
        """
        lion_class = data.pop("lion_class", None)
        if lion_class and lion_class != cls.__name__:
            # Attempt to delegate to a registered subclass
            subcls = get_class(lion_class)
            if subcls and hasattr(subcls, "from_dict") and subcls is not cls:
                return subcls.from_dict(data)
        return cls(**data)

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
    ) -> Node:
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


# File: protocols/graph/node.py
