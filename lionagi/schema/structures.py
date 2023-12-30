import json
from typing import Optional, List, Dict, Any
import networkx as nx
from pydantic import Field
from .base_node import BaseNode
from .relationships import ConditionalRelationship


class Structure(BaseNode):
    nodes: List[BaseNode] = Field(default_factory=list)
    relationships: List[ConditionalRelationship] = Field(default_factory=list)
    graph: 'nx.Graph' = nx.DiGraph()

    def add_node(self, node: BaseNode) -> None:
        self.nodes.append(node)

    def remove_node(self, node_id: str) -> None:
        self.nodes = [node for node in self.nodes if node.get_id() != node_id]
        self.relationships = [rel for rel in self.relationships if rel.target_node_id != node_id and rel.get_id() != node_id]

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        return next((node for node in self.nodes if node.get_id() == node_id), None)

    def add_relationship(self, relationship: ConditionalRelationship) -> None:
        if self.get_node(relationship.get_id()) and self.get_node(relationship.target_node_id):
            self.relationships.append(relationship)

    def remove_relationship(self, relationship_id: str) -> None:
        self.relationships = [rel for rel in self.relationships if rel.get_id() != relationship_id]

    def get_relationships(self, node_id: str) -> List[ConditionalRelationship]:
        return [rel for rel in self.relationships if rel.get_id() == node_id or rel.target_node_id == node_id]

    def evaluate_conditions(self, context: Dict[str, Any]) -> List[ConditionalRelationship]:
        return [rel for rel in self.relationships if all(rel.evaluate_condition(cond, context) for cond in rel.conditions)]
    
    
class Structure:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: BaseNode) -> None:
        self.graph.add_node(node.id_, content=node.content, metadata=node.metadata)

    def add_relationship(self, source_node_id: str, target_node_id: str, relationship: ConditionalRelationship) -> None:
        self.graph.add_edge(source_node_id, target_node_id,
                            label=relationship.label,
                            properties=relationship.properties,
                            condition=relationship.condition)

    def remove_relationship(self, source_node_id: str, target_node_id: str) -> None:
        if self.graph.has_edge(source_node_id, target_node_id):
            self.graph.remove_edge(source_node_id, target_node_id)

    def get_relationships(self, node_id: str) -> list:
        return list(self.graph.edges(node_id, data=True))

    def get_conditional_relationships(self, node_id: str) -> list:
        return [(target_id, data) for _, target_id, data in self.graph.edges(node_id, data=True) if "condition" in data]

    def to_json(self) -> str:
        return json.dumps(nx.node_link_data(self.graph))

    def from_json(self, data: str) -> None:
        graph_data = json.loads(data)
        self.graph = nx.node_link_graph(graph_data)
        