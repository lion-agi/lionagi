from typing import TypeVar
from .graph import Graph
from ..schema import BaseNode
from .relationship import Relationship

T = TypeVar('T', bound='BaseNode')
R = TypeVar('R', bound='Relationship')


class Structure(BaseNode):
    """
    Represents the structure of a graph consisting of nodes and relationships.
    """
    graph: Graph

    def add_node(self, node: T) -> None:
        """
        Adds a node to the structure.
        
        Args:
            node (T): The node instance to be added.
        """
        self.graph.add_node(node)

    def add_relationship(self, relationship: R) -> None:
        """
        Adds a relationship to the structure.
        
        Args:
            relationship (R): The relationship instance to be added.
        """
        self.graph.add_relationship(relationship)

    # type can be dict or list
    # @staticmethod
    # def _typed_return(type: Type[Union[Dict, List]],
    #                   obj: Optional[Dict[str, Any]] = None
    #                   ) -> Union[Dict[str, Any], List[Any]]:
    #     """
    #     Returns the object in the specified type format.
    #
    #     Args:
    #         type (Type[Union[Dict, List]]): The type to return the object as (dict or list).
    #
    #         obj (Optional[Dict[str, Any]]): The object to be converted.
    #
    #     Returns:
    #         Union[Dict[str, Any], List[Any]]: The object in the specified type format.
    #     """
    #     if type is list:
    #         return list(obj.values())
    #     return obj
    
    def get_relationships(self) -> list[R]:
        return self.graph.get_node_relationships()

    def get_node_relationships(self, node: T, out_edge=True) -> R:
        return self.graph.get_node_relationships(node, out_edge)

    def node_exist(self, node: T) -> bool:
        """
        Checks if a node exists in the structure.
        
        Args:
            node (T): The node instance or node ID to check for existence.
            
        Returns:
            bool: True if the node exists, False otherwise.
        """

        return self.graph.node_exist(node)
    
    def relationship_exist(self, relationship: R) -> bool:
        """
        Checks if a relationship exists in the structure.
        
        Args:
            relationship (R): The relationship instance to check for existence.
            
        Returns:
            bool: True if the relationship exists, False otherwise.
        """
        return self.graph.relationship_exists(relationship)

    def remove_node(self, node: T) -> T:
        """
        Removes a node and its associated relationships from the structure.
        
        Args:
            node (T): The node instance or node ID to be removed.
        """
        return self.graph.remove_node(node)

    def remove_relationship(self, relationship: R) -> R:
        """
        Removes a relationship from the structure.
        
        Args:
            relationship (R): The relationship instance to be removed.
        """
        return self.graph.remove_relationship(relationship)
        