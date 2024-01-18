from pydantic import Field
from typing import Dict, Optional, Any
from ..schema.base_node import BaseNode


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
    condition: dict = Field(default={})

    def add_condition(self, condition: Dict[str, Any]) -> None:
        """
        Adds a condition to the relationship.

        Args:
            condition: The condition to be added.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
            >>> relationship.add_condition({"key": "value"})
        """
        self.condition.update(condition)

    def remove_condition(self, condition_key: str) -> Any:
        """
        Removes a condition from the relationship.

        Args:
            condition_key: The key of the condition to be removed.

        Returns:
            The value of the removed condition.

        Raises:
            KeyError: If the condition key is not found.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2", condition={"key": "value"})
            >>> relationship.remove_condition("key")
            'value'
        """
        if condition_key not in self.condition.keys():
            raise KeyError(f'condition {condition_key} is not found')
        return self.condition.pop(condition_key)

    def condition_exists(self, condition_key: str) -> bool:
        """
        Checks if a condition exists in the relationship.

        Args:
            condition_key: The key of the condition to check.

        Returns:
            True if the condition exists, False otherwise.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2", condition={"key": "value"})
            >>> relationship.condition_exists("key")
            True
        """
        if condition_key in self.condition.keys():
            return True
        else:
            return False

    def get_condition(self, condition_key: Optional[str] = None) -> Any:
        """
        Retrieves a specific condition or all conditions of the relationship.

        Args:
            condition_key: The key of the specific condition. If None, all conditions are returned.

        Returns:
            The requested condition or all conditions if no key is provided.

        Raises:
            ValueError: If the specified condition key does not exist.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2", condition={"key": "value"})
            >>> relationship.get_condition("key")
            'value'
            >>> relationship.get_condition()
            {'key': 'value'}
        """
        if condition_key is None:
            return self.condition
        if self.condition_exists(condition_key=condition_key):
            return self.condition[condition_key]
        else:
            raise ValueError(f"Condition {condition_key} does not exist")
    
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
        else :
            raise ValueError(f"Source node {self.target_node_id} does not exist")

    def __str__(self) -> str:
        """
        Returns a simple string representation of the Relationship.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
            >>> str(relationship)
            'Relationship (id_=None, from=node1, to=node2, label=None)'
        """
        return f"Relationship (id_={self.id_}, from={self.source_node_id}, to={self.target_node_id}, label={self.label})"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Relationship.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
            >>> repr(relationship)
            'Relationship(id_=None, from=node1, to=node2, content=None, metadata=None, label=None)'
        """
        return f"Relationship(id_={self.id_}, from={self.source_node_id}, to={self.target_node_id}, content={self.content}, " \
               f"metadata={self.metadata}, label={self.label})"
