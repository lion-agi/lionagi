from pydantic import Field
from typing import Dict, Optional, Any
from ..schema.base_schema import BaseNode


class Relationship(BaseNode):
    """
    Relationship class represents a relationship between two nodes in a graph.

    Inherits from BaseNode and adds functionality to manage conditions and relationships 
    between source and target nodes.

    Attributes:
        source_node_id (str): The identifier of the source node.
        target_node_id (str): The identifier of the target node.
        condition (Dict[str, Any]): A dictionary representing conditions for the relationship.
    """

    source_node_id: str
    target_node_id: str
    condition: dict = Field(default={})

    def add_condition(self, condition: Dict[str, Any]) -> None:
        """
        Adds a condition to the relationship.

        Parameters:
            condition (Dict[str, Any]): The condition to be added.
        """
        self.condition.update(condition)

    def remove_condition(self, condition_key: str) -> Any:
        """
        Removes a condition from the relationship.

        Parameters:
            condition_key (str): The key of the condition to be removed.

        Returns:
            Any: The value of the removed condition.

        Raises:
            KeyError: If the condition key is not found.
        """
        if condition_key not in self.condition.keys():
            raise KeyError(f'condition {condition_key} is not found')
        return self.condition.pop(condition_key)

    def condition_exists(self, condition_key: str) -> bool:
        """
        Checks if a condition exists in the relationship.

        Parameters:
            condition_key (str): The key of the condition to check.

        Returns:
            bool: True if the condition exists, False otherwise.
        """
        if condition_key in self.condition.keys():
            return True
        else:
            return False

    def get_condition(self, condition_key: Optional[str] = None) -> Any:
        """
        Retrieves a specific condition or all conditions of the relationship.

        Parameters:
            condition_key (Optional[str]): The key of the specific condition. Defaults to None.

        Returns:
            Any: The requested condition or all conditions if no key is provided.

        Raises:
            ValueError: If the specified condition key does not exist.
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

        Parameters:
            obj (Dict[str, Any]): The object to check.

        Returns:
            bool: True if the source node exists, False otherwise.
        """
        return self.source_node_id in obj.keys()
    
    def _target_existed(self, obj: Dict[str, Any]) -> bool:
        """
        Checks if the target node exists in a given object.

        Parameters:
            obj (Dict[str, Any]): The object to check.

        Returns:
            bool: True if the target node exists, False otherwise.
        """
        return self.target_node_id in obj.keys()
    
    def _is_in(self, obj: Dict[str, Any]) -> bool:
        """
        Validates the existence of both source and target nodes in a given object.

        Parameters:
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
        