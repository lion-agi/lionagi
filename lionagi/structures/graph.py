import json
import networkx as nx
from ..relationships.relationships import ConditionalRelationship
from ..nodes.base_node import BaseNode


class RelationshipGraph:
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

    def serialize(self) -> str:
        return json.dumps(nx.node_link_data(self.graph))

    def deserialize(self, data: str) -> None:
        graph_data = json.loads(data)
        self.graph = nx.node_link_graph(graph_data)
        