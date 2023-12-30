from typing import List, Optional, Dict, Any
import networkx as nx

from ..schema.base_schema import BaseNode, T, Field
from .relationship import Relationship
   
class Structure(BaseNode):
    nodes: List[T] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    graph: 'nx.Graph' = nx.DiGraph()

    def add_node(self, node: T) -> None:
        self.graph.add_node(node.id_, content=node.content, metadata=node.metadata)

    def remove_node(self, node_id: str) -> None:
        self.nodes = [node for node in self.nodes if node.get_id() != node_id]
        self.relationships = [rel for rel in self.relationships if rel.target_node_id != node_id and rel.get_id() != node_id]

    def get_node(self, node_id: str) -> Optional[T]:
        return next((node for node in self.nodes if node.get_id() == node_id), None)

    def add_relationship(self, relationship: Relationship) -> None:
        if self.get_node(relationship.get_id()) and self.get_node(relationship.target_node_id):
            self.relationships.append(relationship)

    def remove_relationship(self, relationship_id: str) -> None:
        self.relationships = [rel for rel in self.relationships if rel.get_id() != relationship_id]

    def get_relationships(self, node_id: str) -> List[Relationship]:
        return [rel for rel in self.relationships if rel.get_id() == node_id or rel.target_node_id == node_id]

    def evaluate_conditions(self, context: Dict[str, Any]) -> List[Relationship]:
        return [rel for rel in self.relationships if all(rel.evaluate_condition(cond, context) for cond in rel.conditions)]

    def add_relationship(self, source_node_id: str, target_node_id: str, relationship: Relationship) -> None:
        self.graph.add_edge(source_node_id, target_node_id,
                            label=relationship.label,
                            properties=relationship.properties,
                            condition=relationship.condition)

    def remove_relationship(self, source_node_id: str, target_node_id: str) -> None:
        if self.graph.has_edge(source_node_id, target_node_id):
            self.graph.remove_edge(source_node_id, target_node_id)

    def get_relationships(self, node_id: str) -> list:
        return list(self.graph.edges(node_id, data=True))
    
    
