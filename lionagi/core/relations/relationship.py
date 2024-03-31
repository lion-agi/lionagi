from typing import Callable, Dict, Any

from ..schema import BaseNode
from .condition import Condition


class Relationship(BaseNode):
    """
    Represents a relationship between two nodes in a graph.

    Attributes:
        source_node_id (str): The identifier of the source node.
        target_node_id (str): The identifier of the target node.
        condition (Dict[str, Any]): A dictionary representing conditions for the relationship.

    Examples:
        >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
        >>> relationship.add_condition({"key": "value"})
        >>> condition_value = relationship.get_condition("key")
        >>> relationship.remove_condition("key")
    """

    source_node_id: str
    target_node_id: str
    bundle: bool = False
    condition: Callable = None

    def add_condition(self, condition: Condition):
        """
        Adds a condition to the relationship.

        Args:
            condition (Condition): The condition to add.

        Raises:
            ValueError: If the condition is not an instance of the Condition class.
        """
        if not isinstance(condition, Condition):
            raise ValueError(
                "Invalid condition type, please use Condition class to build a valid condition"
            )
        self.condition = condition

    def check_condition(self, source_obj):
        """
        Checks the condition of the relationship.

        Args:
            source_obj: The source object to evaluate the condition against.

        Returns:
            The result of evaluating the condition.

        Raises:
            ValueError: If the relationship condition function is invalid.
        """
        try:
            return bool(self.condition(source_obj))
        except:
            raise ValueError("Invalid relationship condition function")

    def _source_existed(self, obj: Dict[str, Any]) -> bool:
        """
        Checks if the source node exists in a given object.

        Args:
            obj (Dict[str, Any]): The object to check.

        Returns:
            bool: True if the source node exists, False otherwise.
        """
        return self.source_node_id in obj.keys()

    def _target_existed(self, obj: Dict[str, Any]) -> bool:
        """
        Checks if the target node exists in a given object.

        Args:
            obj (Dict[str, Any]): The object to check.

        Returns:
            bool: True if the target node exists, False otherwise.
        """
        return self.target_node_id in obj.keys()

    def _is_in(self, obj: Dict[str, Any]) -> bool:
        """
        Validates the existence of both source and target nodes in a given object.

        Args:
            obj (Dict[str, Any]): The object to check.

        Returns:
            bool: True if both nodes exist.

        Raises:
            ValueError: If either the source or target node does not exist.
        """
        if self._source_existed(obj) and self._target_existed(obj):
            return True

        elif self._source_existed(obj):
            raise ValueError(f"Target node {self.source_node_id} does not exist")
        else:
            raise ValueError(f"Source node {self.target_node_id} does not exist")

    def __str__(self) -> str:
        """
        Returns a simple string representation of the Relationship.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
            >>> str(relationship)
            'Relationship (id_=None, from=node1, to=node2, label=None)'
        """
        return (
            f"Relationship (id_={self.id_}, from={self.source_node_id}, to={self.target_node_id}, "
            f"label={self.label})"
        )

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Relationship.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
            >>> repr(relationship)
            'Relationship(id_=None, from=node1, to=node2, content=None, metadata=None, label=None)'
        """
        return (
            f"Relationship(id_={self.id_}, from={self.source_node_id}, to={self.target_node_id}, "
            f"content={self.content}, metadata={self.metadata}, label={self.label})"
        )
