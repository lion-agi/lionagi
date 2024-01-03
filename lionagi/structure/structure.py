from typing import TypeVar, Dict, Optional, Any, Type, Union, List
from pydantic import Field
from ..schema.base_schema import BaseNode
from .relationship import Relationship

T = TypeVar('T', bound='BaseNode')
R = TypeVar('R', bound='Relationship')


class Structure(BaseNode):
    """
    Represents the structure of a graph consisting of nodes and relationships.
    """
    nodes: Dict[str, T] = Field(default_factory=dict)
    relationships: Dict[str, R] = Field(default_factory=dict)
    node_relationships: Dict[str, Dict[str, Dict[str, str]]] = Field(default_factory=dict)

    def add_node(self, node: T) -> None:
        """
        Adds a node to the structure.
        
        Args:
            node (T): The node instance to be added.
        """
        self.nodes[node.id_] = node
        self.node_relationships[node.id_] = {'in': {}, 'out': {}}

    def add_relationship(self, relationship: R) -> None:
        """
        Adds a relationship to the structure.
        
        Args:
            relationship (R): The relationship instance to be added.
        """
        id_, source_, target_ = (
            relationship.id_, relationship.source_node_id, relationship.target_node_id
            )
        
        self.relationships.update({id_ : relationship})
        self.node_relationships[source_]['out'].update({id_ : target_})
        self.node_relationships[target_]['in'].update({id_ : source_})

    # type can be dict or list
    @staticmethod
    def _typed_return(type: Type[Union[Dict, List]], 
                      obj: Optional[Dict[str, Any]] = None
                      ) -> Union[Dict[str, Any], List[Any]]:
        """
        Returns the object in the specified type format.
        
        Args:
            type (Type[Union[Dict, List]]): The type to return the object as (dict or list).
            
            obj (Optional[Dict[str, Any]]): The object to be converted.
            
        Returns:
            Union[Dict[str, Any], List[Any]]: The object in the specified type format.
        """
        if type is list:
            return list(obj.values())
        return obj
    
    def get_relationships(self, type: Type = dict) -> Union[Dict[str, R], List[R]]:
        """
        Returns the relationships in the specified type format.
        
        Args:
            type (Type): The type to return the relationships as (dict or list).
            
        Returns:
            Union[Dict[str, R], List[R]]: The relationships in the specified type format.
        """
        return self._typed_return(self.relationships, type=type)
        
    def get_node_relationships(self, id_: str, in_out: str, type: Type = dict
                               ) -> Union[Dict[str, str], List[str]]:
        """
        Returns the relationships of a node in the specified type format.
        
        Args:
            id_ (str): The ID of the node.
            
            in_out (str): 'in' for incoming relationships, 'out' for outgoing relationships.
            
            type (Type): The type to return the relationships as (dict or list).
            
        Returns:
            Union[Dict[str, str], List[str]]: The relationships of the node in the specified type format.
        """
        node_relationships = self.node_relationships[id_][in_out]
        return self._typed_return(node_relationships, type=type)

    def node_exist(self, node: Union[T, str]) -> bool:
        """
        Checks if a node exists in the structure.
        
        Args:
            node (Union[T, str]): The node instance or node ID to check for existence.
            
        Returns:
            bool: True if the node exists, False otherwise.
        """

        return node.id_ in self.nodes.keys()
    
    def relationship_exist(self, relationship: R) -> bool:
        """
        Checks if a relationship exists in the structure.
        
        Args:
            relationship (R): The relationship instance to check for existence.
            
        Returns:
            bool: True if the relationship exists, False otherwise.
        """
        return relationship.id_ in self.relationships.keys()
        
    def remove_node_relationships(self, relationship_dict: Dict[str, str], in_out: str) -> None:
        """
        Removes relationships of a node from the structure.
        
        Args:
            relationship_dict (Dict[str, str]): A dictionary of relationship IDs to node IDs.
            
            in_out (str): 'in' to remove incoming relationships, 'out' to remove outgoing relationships.
        """
        for relationship_id, node_id in relationship_dict.items():
            self.node_relationships[node_id][in_out].pop(relationship_id)
            self.relationships.pop(relationship_id)

    def remove_node(self, node: Union[T, str]) -> None:
        """
        Removes a node and its associated relationships from the structure.
        
        Args:
            node (Union[T, str]): The node instance or node ID to be removed.
        """
        node_id = node if isinstance(node, str) else node.id_
        out_ = self.get_node_relationships(node_id, 'out')
        in_ = self.get_node_relationships(node_id, 'in')
        
        self.remove_node_relationships(out_, 'in')
        self.remove_node_relationships(in_, 'out')
        self.node_relationships.pop(node_id)

    def remove_relationship(self, relationship: R) -> None:
        """
        Removes a relationship from the structure.
        
        Args:
            relationship (R): The relationship instance to be removed.
        """
        id_, source_, target_ = (relationship.id_, 
                                 relationship.source_node_id, 
                                 relationship.target_node_id)
        
        self.node_relationships[source_]['out'].pop(id_)
        self.node_relationships[target_]['in'].pop(id_)
        self.relationships.pop(id_)
        