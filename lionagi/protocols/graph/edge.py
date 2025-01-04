# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from lionagi.utils import is_same_dtype

from .._concepts import Condition, Relational
from ..generic.element import ID, Element, IDType

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
    An edge in a graph, connecting a head Node to a tail Node. Optional
    EdgeCondition can control traversal. Additional properties like labels,
    metadata, etc., may be stored in `properties`.
    """

    head: IDType
    tail: IDType
    properties: dict[str, Any] = Field(
        default_factory=dict,
        title="Properties",
        description="Custom properties associated with this edge.",
    )

    def __init__(
        self,
        head: ID[Relational].Ref,
        tail: ID[Relational].Ref,
        condition: EdgeCondition | None = None,
        label: list[str] | None = None,
        **kwargs,
    ):
        """
        Initialize an Edge.

        This constructor sets up an edge by linking a head node to a tail node,
        with optional conditions and labels. Additional properties can also be
        provided via keyword arguments.

        Args:
            head (Relational | str): The head node or its ID. This is the
                starting point of the edge.
            tail (Relational | str): The tail node or its ID. This is the end
                point of the edge.
            condition (EdgeCondition | None): An optional condition that must
                be satisfied for the edge to be traversed.
            label (list[str] | None): An optional list of labels that describe
                the edge.
            kwargs: Optional additional properties for the edge.
        """
        head = ID.get_id(head)
        tail = ID.get_id(tail)
        if condition:
            if not isinstance(condition, EdgeCondition):
                raise ValueError(
                    "Condition must be an instance of EdgeCondition."
                )
            kwargs["condition"] = condition
        if label:
            if isinstance(label, str):
                kwargs["label"] = [label]
            elif isinstance(label, list) and is_same_dtype(label, str):
                kwargs["label"] = label
            else:
                raise ValueError(
                    "Label must be a string or a list of strings."
                )

        super().__init__(head=head, tail=tail, properties=kwargs)

    @field_serializer("head", "tail")
    def _serialize_id(self, value: IDType) -> str:
        return str(value)

    @field_validator("head", "tail", mode="before")
    def _validate_id(cls, value: str) -> IDType:
        return ID.get_id(value)

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
        if not value:
            self.properties["label"] = []
            return
        if isinstance(value, str):
            self.properties["label"] = [value]
            return
        if isinstance(value, list) and is_same_dtype(value, str):
            self.properties["label"] = value
            return
        raise ValueError("Label must be a string or a list of strings.")

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
