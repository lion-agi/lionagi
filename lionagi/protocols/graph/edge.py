# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..generic._id import ID
from ..generic.element import Element
from ..generic.event import Condition
from ..generic.node import Node

__all__ = (
    "EdgeCondition",
    "Edge",
)


class EdgeCondition(BaseModel, Condition):
    """Represents a condition associated with an edge in the Lion framework.

    This class combines Condition characteristics with Pydantic's
    BaseModel for robust data validation and serialization.

    Attributes:
        source (Any): The source for condition evaluation.
    """

    source: Any = Field(
        default=None,
        title="Source",
        description="The source for condition evaluation",
    )

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )


class Edge(Element):
    """
    Represents an edge in a graph structure.

    An edge connects a head node to a tail node and can store additional
    properties such as conditions and labels. It is used to model relationship
    between nodes in graph-based data structures.

    Attributes:
        properties (Note): Stores additional properties of the edge. This can
            include conditions that must be met for the edge to be traversed
            and labels that describe the edge.
        head (str): The ID of the head node in the graph.
        tail (str): The ID of the tail node in the graph.
    """

    properties: dict = Field(default_factory=dict)
    head: ID[Node].ID
    tail: ID[Node].ID

    def __init__(
        self,
        head: ID[Node].Ref,
        tail: ID[Node].Ref,
        condition: EdgeCondition | None = None,
        label: list[str] | None = None,
        **kwargs,
    ):
        head = ID.get_id(head)
        tail = ID.get_id(tail)

        super().__init__(head=head, tail=tail)

        # Initialize properties
        if condition:
            self.properties["condition"] = condition
        if label:
            self.properties["label"] = label
        for key, value in kwargs.items():
            self.properties[key] = value

    async def check_condition(self, *args, **kwargs) -> bool:
        """
        Check if the edge's condition is satisfied.

        This method checks whether the edge can be traversed by evaluating its
        condition. If no condition is specified, the edge is considered
        traversable by default.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: True if the condition is satisfied or if no condition exists,
                  False otherwise.
        """
        condition: EdgeCondition | None = self.properties.get(
            "condition", None
        )
        if condition:
            return await condition.apply(*args, **kwargs)
        return True  # If no condition exists, the edge is always traversable

    def update_property(self, key: str, value: Any) -> None:
        """
        Update a property value directly.

        Args:
            key: The property key to update.
            value: The new value for the property.
        """
        self.properties[key] = value

    def update_condition_source(self, source: dict) -> None:
        """
        Update the condition source.

        Args:
            source: The new source dictionary for the condition.
        """
        condition: EdgeCondition | None = self.properties.get(
            "condition", None
        )
        if condition:
            condition.source = source


__all__ = ["Edge"]
