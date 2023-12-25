import json
from typing import Any, Dict, Optional, Union
from uuid import uuid4

import networkx as nx
from pydantic import BaseModel, Field


class BaseNode(BaseModel):
    """
    Represents the base structure of a graph node.

    Args:
        BaseModel (pydantic.BaseModel): Pydantic BaseModel class for data validation.

    Attributes:
        id_ (str): Unique node identifier, auto-generated using uuid4().
        label (Optional[str]): Optional label for the node.
        content (Union[str, Dict[str, Any], None]): Content of the node.
        metadata (Dict[str, Any]): Additional metadata about the node.
    """
    id_: str = Field(default_factory=lambda: str(uuid4()), alias="node_id")
    label: Optional[str] = None
    content: Union[str, Dict[str, Any], None] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def class_name(cls) -> str:
        """
        Get the class name.

        Returns:
            str: Name of the class.
        """
        return cls.__name__

    def to_json(self) -> str:
        """
        Serialize the node instance to a JSON string.

        Returns:
            str: JSON string representing the node instance.
        """
        return json.dumps(self.dict(by_alias=True))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node instance to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representing the node instance.
        """
        return self.dict(by_alias=True)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseNode":
        """
        Create a BaseNode instance from a JSON string.

        Args:
            json_str (str): JSON string to deserialize.

        Returns:
            BaseNode: An instance of `BaseNode`.
        """
        data = json.loads(json_str)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        """
        Create a BaseNode instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary of node data.

        Returns:
            BaseNode: An instance of `BaseNode`.
        """
        return cls(**data)


class ConditionalRelationship(BaseModel):
    """
    Represents a conditional relationship between two nodes in a graph.

    Attributes:
        target_node_id (str): Identifier of the target node.
        properties (Dict[str, Any]): Properties associated with the relationship.
        condition (Optional[str]): Condition that must be satisfied for the relationship to take effect.
    """
    target_node_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    condition: Optional[str] = None

    def check_condition(self, context: Dict[str, Any]) -> bool:
        """
        Check if the condition is satisfied based on the provided context.

        Args:
            context (Dict[str, Any]): Context to evaluate the condition against.

        Returns:
            bool: `True` if condition is satisfied, `False` otherwise.
        """
        return context.get(self.condition, False)


class GraphNode(BaseNode):
    """
    Represents a node within a graph including its relationships.

    Inherits from BaseNode and includes additional attributes and methods
    for graph relation handling.

    Attributes:
        graph (nx.DiGraph): Directed graph instance from networkx library.

    Nested Classes:
        Config: Configuration for pydantic model to allow for the networkx DiGraph type.

    Methods:
        add_relationship: Add a directed relationship to another node.
        remove_relationship: Remove a relationship with another node.
        get_relationships: Get all relationships from this node.
        get_conditional_relationships: Get all relationships with conditions.
    """
    graph: nx.DiGraph = Field(default_factory=nx.DiGraph)

    class Config:
        arbitrary_types_allowed = True

    def add_relationship(self, target_node_id: str, relationship_type: str, properties: Optional[Dict[str, Any]] = None, condition: Optional[str] = None) -> None:
        """
        Add a relationship (edge) to the graph.

        Args:
            target_node_id (str): Identifier of the target node.
            relationship_type (str): Type of the relationship.
            properties (Optional[Dict[str, Any]]): Properties of the relationship.
            condition (Optional[str]): Condition to be associated with the relationship.
        """
        properties = properties or {}
        if condition:
            properties["condition"] = condition
        self.graph.add_edge(self.id_, target_node_id, relationship_type=relationship_type, **properties)

    def remove_relationship(self, target_node_id: str) -> None:
        """
        Remove an existing relationship (edge) from the graph.

        Args:
            target_node_id (str): Identifier of the target node.
        """
        if self.graph.has_edge(self.id_, target_node_id):
            self.graph.remove_edge(self.id_, target_node_id)

    def get_relationships(self) -> list:
        """
        Retrieve all relationships (edges) from this node.

        Returns:
            list: A list of tuples representing the edges and their associated data.
        """
        return list(self.graph.edges(self.id_, data=True))

    def get_conditional_relationships(self) -> list:
        """
        Retrieve relationships (edges) with conditions from this node.

        Returns:
            list: A list of tuples with conditional edges and their data.
        """
        return [(target_id, data) for _, target_id, data in self.graph.edges(self.id_, data=True) if "condition" in data]
