from typing import TypeVar
from pydantic import Field
from lionagi.schema.base_schema import BaseNode, T
from .relationship import Relationship

R = TypeVar('R', bound='Relationship')


class Structure(BaseNode):
    
    nodes: dict = Field(default_factory=dict)
    relationships: dict = Field(default_factory=dict)
    node_relationships: dict = Field(default_factory=dict)

    def add_node(self, node: T):
        self.nodes[node.id_] = node
        self.node_relationships[node.id_] = {'in': {}, 'out': {}}

    def add_relationship(self, relationship: R):
        id_, source_, target_ = (relationship.id_, 
                                 relationship.source_node_id, 
                                 relationship.target_node_id)
        
        self.relationships.update({id_ : relationship})
        self.node_relationships[source_]['out'].update({id_ : target_})
        self.node_relationships[target_]['in'].update({id_ : source_})

    # type can be dict or list
    @staticmethod
    def _typed_return(type=dict, obj=None):
        if type is list:
            return list(obj.values())
        return obj
    
    def get_relationships(self, type=dict):
        return self._typed_return(self.relationships, type=type)
        
    def get_node_relationships(self, id_, in_out, type=dict):
        node_relationships = self.node_relationships[id_][in_out]
        return self._typed_return(node_relationships, type=type)

    def node_exist(self, node):
        return node.id_ in self.nodes.keys()
    
    def relationship_exist(self, relationship: R):
        return relationship.id_ in self.relationships.keys()
        
    def remove_node_relationships(self, relationship_dict, in_out):
        for relationship_id, node_id in relationship_dict.items():
            self.node_relationships[node_id][in_out].pop(relationship_id)
            self.relationships.pop(relationship_id)

    def remove_node(self, node):
        node_id = node if isinstance(node, str) else node.id_
        out_ = self.get_node_relationships(node_id, 'out')
        in_ = self.get_node_relationships(node_id, 'in')
        
        self.remove_node_relationships(out_, 'in')
        self.remove_node_relationships(in_, 'out')
        self.node_relationships.pop(node_id)

    def remove_relationship(self, relationship: R):
        id_, source_, target_ = (relationship.id_, 
                                 relationship.source_node_id, 
                                 relationship.target_node_id)
        
        self.node_relationships[source_]['out'].pop(id_)
        self.node_relationships[target_]['in'].pop(id_)
        self.relationships.pop(id_)
        