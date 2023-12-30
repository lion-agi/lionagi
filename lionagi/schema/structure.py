from typing import Optional, List, Dict, Any
from pydantic import Field
from .base_node import BaseNode
from .relationship import ConditionalRelationship


class Structure(BaseNode):
    nodes: List[BaseNode] = Field(default_factory=list)
    relationships: List[ConditionalRelationship] = Field(default_factory=list)

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