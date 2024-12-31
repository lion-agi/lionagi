# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from .._concepts import Condition, Relational
from ..generic.element import ID, Element

__all__ = (
    "EdgeCondition",
    "Edge",
)


class EdgeCondition(Condition):
    """
    Represents a condition associated with an Edge. Subclasses must
    implement `apply` to determine whether the edge is traversable.
    """

    def __init__(self, source: Any = None):
        self.source = source

    async def apply(self, *args, **kwargs) -> bool:
        """
        Evaluate this condition asynchronously. By default, raises
        NotImplementedError. Override in subclasses.

        Returns:
            bool: True if condition is met, else False.
        """
        raise NotImplementedError("Subclasses must implement `apply`.")


class Edge(Element):
    """
    An edge in a graph, connecting a head Node to a tail Node. Optional
    EdgeCondition can control traversal. Additional properties like labels,
    metadata, etc., may be stored in `properties`.
    """

    def __init__(
        self,
        head: ID[Relational].Ref,
        tail: ID[Relational].Ref,
        condition: EdgeCondition | None = None,
        label: list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Args:
            head (ID[Node].Ref):
                A reference (ID, Node, or string) to the head node.
            tail (ID[Node].Ref):
                A reference to the tail node.
            condition (EdgeCondition | None):
                Optional condition controlling edge traversal.
            label (list[str] | None):
                Optional list of labels describing the edge.
            **kwargs:
                Additional properties stored in `self.properties`.
        """
        super().__init__()
        self.head = ID.get_id(head)
        self.tail = ID.get_id(tail)
        self.properties: dict[str, Any] = {}

        if condition:
            self.condition = condition

        if label:
            self.label = [label] if not isinstance(label, list) else label

        for k, v in kwargs.items():
            self.properties[k] = v

    @property
    def label(self) -> list[str] | None:
        return self.properties.get("label", None)

    @property
    def condition(self) -> EdgeCondition | None:
        return self.properties.get("condition", None)

    @condition.setter
    def condition(self, value: EdgeCondition | None) -> None:
        if not isinstance(value, EdgeCondition):
            raise ValueError("Condition must be an instance of EdgeCondition.")
        self.properties["condition"] = value

    @label.setter
    def label(self, value: list[str] | None) -> None:
        if not isinstance(value, list):
            raise ValueError("Label must be a list of strings.")
        self.properties["label"] = value

    async def check_condition(self, *args, **kwargs) -> bool:
        """
        Check if this edge can be traversed, by evaluating any assigned condition.

        Returns:
            bool: True if condition is met or if no condition exists.
        """
        if self.condition:
            return await self.condition.apply(*args, **kwargs)
        return True

    def update_property(self, key: str, value: Any) -> None:
        """Update or add a custom property in `self.properties`."""
        self.properties[key] = value

    def update_condition_source(self, source: Any) -> None:
        """Update the `.source` attribute in the assigned EdgeCondition, if any."""
        cond: EdgeCondition | None = self.properties.get("condition", None)
        if cond:
            cond.source = source


# File: protocols/graph/edge.py
