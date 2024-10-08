from lionabc import Relational
from pydantic import Field, field_serializer

from lion_core.generic.element import Element
from lion_core.generic.note import Note
from lion_core.graph.edge_condition import EdgeCondition
from lion_core.sys_utils import SysUtil


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

    properties: Note = Field(default_factory=Note)
    head: str = Field(...)
    tail: str = Field(...)

    def __init__(
        self,
        head: Relational | str,
        tail: Relational | str,
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
        head = SysUtil.get_id(head)
        tail = SysUtil.get_id(tail)

        super().__init__(head=head, tail=tail)
        if condition:
            self.properties.set("condition", condition)
        if label:
            self.properties.set("label", label)
        self.properties.update([], kwargs)

    @field_serializer("properties")
    def _serialize_properties(self, value):
        """
        Serialize the properties of the edge.

        This method converts the `properties` field into a format suitable for
        storage or transmission, typically as part of serialization to JSON or
        other formats.

        Args:
            value: The properties Note to serialize.

        Returns:
            The serialized properties.
        """
        return value.content

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


__all__ = ["Edge"]

# File: lion_core/graph/edge.py
