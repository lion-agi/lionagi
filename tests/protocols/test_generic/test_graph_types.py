import pytest

from lionagi.protocols.graph.graph import Edge, Graph

from .test_graph_base import TestNode


class TypeANode(TestNode):
    """Test node type A"""

    def __init__(self, value: int):
        super().__init__()
        self.add_field("value", value)


class TypeBNode(TestNode):
    """Test node type B"""

    def __init__(self, name: str):
        super().__init__()
        self.add_field("name", name)


class WeightedEdge(Edge):
    """Test weighted edge type"""

    def __init__(self, head, tail, weight: float):
        super().__init__(head=head, tail=tail)
        self.update_property("weight", weight)

    @property
    def weight(self) -> float:
        return self.properties.get("weight")


class LabeledEdge(Edge):
    """Test labeled edge type"""

    def __init__(self, head, tail, labels: list[str]):
        super().__init__(head=head, tail=tail)
        self.update_property("labels", labels)

    @property
    def labels(self) -> list[str]:
        return self.properties.get("labels")


@pytest.fixture
def mixed_type_graph():
    """Fixture for graph with mixed node and edge types"""
    graph = Graph()

    # Create different types of nodes
    node_a1 = TypeANode(value=10)
    node_a2 = TypeANode(value=20)
    node_b1 = TypeBNode(name="B1")
    node_b2 = TypeBNode(name="B2")

    # Add nodes
    for node in [node_a1, node_a2, node_b1, node_b2]:
        graph.add_node(node)

    # Create different types of edges
    edge1 = WeightedEdge(head=node_a1, tail=node_b1, weight=5.0)
    edge2 = LabeledEdge(
        head=node_a2, tail=node_b2, labels=["test", "connection"]
    )

    # Add edges
    for edge in [edge1, edge2]:
        graph.add_edge(edge)
        node = graph.internal_nodes[edge.head]
        node.add_relation(edge, "out")
        node = graph.internal_nodes[edge.tail]
        node.add_relation(edge, "in")

    return (
        graph,
        {
            "node_a1": node_a1,
            "node_a2": node_a2,
            "node_b1": node_b1,
            "node_b2": node_b2,
        },
        {"edge1": edge1, "edge2": edge2},
    )


class TestNodeTypes:
    """Test different node types in graph"""

    def test_type_a_nodes(self, mixed_type_graph):
        """Test TypeA nodes"""
        graph, nodes, _ = mixed_type_graph

        # Verify TypeA nodes
        node_a1 = nodes["node_a1"]
        node_a2 = nodes["node_a2"]

        assert isinstance(node_a1, TypeANode)
        assert isinstance(node_a2, TypeANode)
        assert node_a1.value == 10
        assert node_a2.value == 20

    def test_type_b_nodes(self, mixed_type_graph):
        """Test TypeB nodes"""
        graph, nodes, _ = mixed_type_graph

        # Verify TypeB nodes
        node_b1 = nodes["node_b1"]
        node_b2 = nodes["node_b2"]

        assert isinstance(node_b1, TypeBNode)
        assert isinstance(node_b2, TypeBNode)
        assert node_b1.name == "B1"
        assert node_b2.name == "B2"

    def test_node_type_fields(self, mixed_type_graph):
        """Test node type specific fields"""
        graph, nodes, _ = mixed_type_graph

        # Test TypeA specific field
        node_a1 = nodes["node_a1"]
        node_a1.value = 30
        assert graph.internal_nodes[node_a1.id].value == 30

        # Test TypeB specific field
        node_b1 = nodes["node_b1"]
        node_b1.name = "NewB1"
        assert graph.internal_nodes[node_b1.id].name == "NewB1"


class TestEdgeTypes:
    """Test different edge types in graph"""

    def test_weighted_edges(self, mixed_type_graph):
        """Test WeightedEdge type"""
        graph, _, edges = mixed_type_graph
        edge1 = edges["edge1"]

        assert isinstance(edge1, WeightedEdge)
        assert edge1.weight == 5.0

        # Test weight modification
        edge1.update_property("weight", 7.5)
        assert graph.internal_edges[edge1.id].weight == 7.5

    def test_labeled_edges(self, mixed_type_graph):
        """Test LabeledEdge type"""
        graph, _, edges = mixed_type_graph
        edge2 = edges["edge2"]

        assert isinstance(edge2, LabeledEdge)
        assert "test" in edge2.labels
        assert "connection" in edge2.labels

        # Test labels modification
        new_labels = edge2.labels + ["new_label"]
        edge2.update_property("labels", new_labels)
        assert "new_label" in graph.internal_edges[edge2.id].labels


class TestMixedTypeOperations:
    """Test operations with mixed node and edge types"""

    def test_mixed_type_traversal(self, mixed_type_graph):
        """Test traversal with mixed types"""
        graph, nodes, _ = mixed_type_graph

        # Get successors of TypeA nodes
        node_a1 = nodes["node_a1"]
        successors = graph.get_successors(node_a1)
        assert len(successors) == 1
        assert isinstance(successors[0], TypeBNode)

        # Get predecessors of TypeB nodes
        node_b1 = nodes["node_b1"]
        predecessors = graph.get_predecessors(node_b1)
        assert len(predecessors) == 1
        assert isinstance(predecessors[0], TypeANode)

    def test_mixed_edge_finding(self, mixed_type_graph):
        """Test finding different edge types"""
        graph, nodes, _ = mixed_type_graph

        # Find edges from node_a1
        node_a1 = nodes["node_a1"]
        edges = graph.find_node_edge(node_a1, direction="out")
        assert len(edges) == 1
        assert isinstance(edges[0], WeightedEdge)

        # Find edges from node_a2
        node_a2 = nodes["node_a2"]
        edges = graph.find_node_edge(node_a2, direction="out")
        assert len(edges) == 1
        assert isinstance(edges[0], LabeledEdge)


class TestComplexTypes:
    """Test complex type scenarios"""

    def test_nested_type_node(self):
        """Test node with nested type structure"""

        class NestedNode(TestNode):
            def __init__(self, data: dict):
                super().__init__()
                self.add_field("data", data)

        graph = Graph()
        nested_data = {"level1": {"level2": {"value": 42}}}
        node = NestedNode(data=nested_data)
        graph.add_node(node)

        retrieved_node = graph.internal_nodes[node.id]
        assert retrieved_node.data["level1"]["level2"]["value"] == 42

    def test_composite_edge(self):
        """Test edge with composite properties"""

        class CompositeEdge(Edge):
            def __init__(self, head, tail, metadata: dict):
                super().__init__(head=head, tail=tail)
                for key, value in metadata.items():
                    self.update_property(key, value)

        graph = Graph()
        node1 = TypeANode(value=1)
        node2 = TypeANode(value=2)
        graph.add_node(node1)
        graph.add_node(node2)

        metadata = {
            "weights": [1.0, 2.0, 3.0],
            "labels": ["a", "b", "c"],
            "config": {"key": "value"},
        }
        edge = CompositeEdge(head=node1, tail=node2, metadata=metadata)
        graph.add_edge(edge)

        retrieved_edge = graph.internal_edges[edge.id]
        assert retrieved_edge.properties.get("weights") == [1.0, 2.0, 3.0]
        assert retrieved_edge.properties.get("labels") == ["a", "b", "c"]
        assert retrieved_edge.properties.get("config")["key"] == "value"

    def test_inheritance_chain(self):
        """Test deep inheritance chain for nodes and edges"""

        class BaseCustomNode(TestNode):
            def __init__(self):
                super().__init__()
                self.add_field("base_field", "base")

        class MidCustomNode(BaseCustomNode):
            def __init__(self):
                super().__init__()
                self.add_field("mid_field", "mid")

        class FinalCustomNode(MidCustomNode):
            def __init__(self):
                super().__init__()
                self.add_field("final_field", "final")

        graph = Graph()
        node = FinalCustomNode()
        graph.add_node(node)

        retrieved_node = graph.internal_nodes[node.id]
        assert retrieved_node.base_field == "base"
        assert retrieved_node.mid_field == "mid"
        assert retrieved_node.final_field == "final"

    def test_dynamic_type_creation(self):
        """Test dynamically created node and edge types"""
        graph = Graph()

        # Dynamically create node type
        dynamic_node_attrs = {"custom_field": "value", "number": 42}

        class DynamicNode(TestNode):
            pass

        node = DynamicNode()
        for key, value in dynamic_node_attrs.items():
            node.add_field(key, value)

        graph.add_node(node)

        # Verify dynamic fields
        retrieved_node = graph.internal_nodes[node.id]
        for key, value in dynamic_node_attrs.items():
            assert getattr(retrieved_node, key) == value
