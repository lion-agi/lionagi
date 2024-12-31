# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from pydantic import Field, field_serializer, field_validator

from lionagi.utils import is_same_dtype

from .._concepts import Condition
from ..generic.element import ID, Element, IDType

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

    head: IDType
    tail: IDType
    properties: dict[str, Any] = Field(
        default_factory=dict,
        title="Properties",
        description="Custom properties associated with this edge.",
    )

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
