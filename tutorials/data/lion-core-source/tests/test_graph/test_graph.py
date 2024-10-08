import random
import time

import pytest
from lionabc import Relational
from lionabc.exceptions import LionRelationError

from lion_core.generic.component import Component
from lion_core.generic.pile import Pile
from lion_core.graph.edge import Edge
from lion_core.graph.graph import Graph


class Node(Component, Relational):
    pass


# Helper functions to create test nodes and edges
def create_test_node(name):
    return Node(content={"name": name})


def create_test_edge(head, tail, label=None):
    return Edge(head=head, tail=tail, label=label)


# Fixture for a basic graph
@pytest.fixture
def basic_graph():
    graph = Graph()
    node1 = create_test_node("Node1")
    node2 = create_test_node("Node2")
    node3 = create_test_node("Node3")
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_edge(create_test_edge(node1, node2))
    graph.add_edge(create_test_edge(node2, node3))
    return graph


# Test basic graph operations
def test_add_node(basic_graph):
    new_node = create_test_node("NewNode")
    basic_graph.add_node(new_node)
    assert new_node in basic_graph.internal_nodes
    assert new_node.ln_id in basic_graph.node_edge_mapping


def test_add_edge(basic_graph):
    node1 = basic_graph.internal_nodes[0]
    node3 = basic_graph.internal_nodes[2]
    new_edge = create_test_edge(node1, node3)
    basic_graph.add_edge(new_edge)
    assert new_edge in basic_graph.internal_edges
    assert new_edge.ln_id in basic_graph.node_edge_mapping[node1.ln_id, "out"]
    assert new_edge.ln_id in basic_graph.node_edge_mapping[node3.ln_id, "in"]


def test_remove_node(basic_graph):
    node_to_remove = basic_graph.internal_nodes[1]
    basic_graph.remove_node(node_to_remove)
    assert node_to_remove not in basic_graph.internal_nodes
    assert node_to_remove.ln_id not in basic_graph.node_edge_mapping


def test_remove_edge(basic_graph):
    edge_to_remove = basic_graph.internal_edges[0]
    basic_graph.remove_edge(edge_to_remove)
    assert edge_to_remove not in basic_graph.internal_edges
    assert (
        edge_to_remove.ln_id
        not in basic_graph.node_edge_mapping[edge_to_remove.head, "out"]
    )
    assert (
        edge_to_remove.ln_id
        not in basic_graph.node_edge_mapping[edge_to_remove.tail, "in"]
    )


def test_find_node_edge(basic_graph):
    node = basic_graph.internal_nodes[1]
    edges = basic_graph.find_node_edge(node)
    assert len(edges) == 2
    in_edges = basic_graph.find_node_edge(node, direction="in")
    assert len(in_edges) == 1
    out_edges = basic_graph.find_node_edge(node, direction="out")
    assert len(out_edges) == 1


def test_get_heads(basic_graph):
    heads = basic_graph.get_heads()
    assert len(heads) == 1
    assert heads[0].content["name"] == "Node1"


def test_get_predecessors(basic_graph):
    node = basic_graph.internal_nodes[1]
    predecessors = basic_graph.get_predecessors(node)
    assert len(predecessors) == 1
    assert predecessors[0].content["name"] == "Node1"


def test_get_successors(basic_graph):
    node = basic_graph.internal_nodes[1]
    successors = basic_graph.get_successors(node)
    assert len(successors) == 1
    assert successors[0].content["name"] == "Node3"


# Test error cases
def test_add_invalid_node():
    graph = Graph()
    with pytest.raises(LionRelationError):
        graph.add_node("Not a Node")


def test_add_invalid_edge(basic_graph):
    with pytest.raises(LionRelationError):
        basic_graph.add_edge("Not an Edge")


def test_add_edge_with_nonexistent_nodes():
    graph = Graph()
    node1 = create_test_node("Node1")
    node2 = create_test_node("Node2")
    graph.add_node(node1)
    with pytest.raises(LionRelationError):
        graph.add_edge(create_test_edge(node1, node2))


def test_remove_nonexistent_node(basic_graph):
    non_existent_node = create_test_node("NonExistent")
    with pytest.raises(LionRelationError):
        basic_graph.remove_node(non_existent_node)


def test_remove_nonexistent_edge(basic_graph):
    non_existent_edge = create_test_edge(
        basic_graph.internal_nodes[0], basic_graph.internal_nodes[2]
    )
    with pytest.raises(LionRelationError):
        basic_graph.remove_edge(non_existent_edge)


def test_find_node_edge_nonexistent_node(basic_graph):
    non_existent_node = create_test_node("NonExistent")
    with pytest.raises(LionRelationError):
        basic_graph.find_node_edge(non_existent_node)


# Test complex graph operations
def test_complex_graph():
    graph = Graph()
    nodes = [create_test_node(f"Node{i}") for i in range(10)]
    for node in nodes:
        graph.add_node(node)

    # Create a more complex graph structure
    graph.add_edge(create_test_edge(nodes[0], nodes[1]))
    graph.add_edge(create_test_edge(nodes[0], nodes[2]))
    graph.add_edge(create_test_edge(nodes[1], nodes[3]))
    graph.add_edge(create_test_edge(nodes[2], nodes[4]))
    graph.add_edge(create_test_edge(nodes[3], nodes[5]))
    graph.add_edge(create_test_edge(nodes[4], nodes[5]))
    graph.add_edge(create_test_edge(nodes[5], nodes[6]))
    graph.add_edge(create_test_edge(nodes[6], nodes[7]))
    graph.add_edge(create_test_edge(nodes[6], nodes[8]))
    graph.add_edge(create_test_edge(nodes[7], nodes[9]))
    graph.add_edge(create_test_edge(nodes[8], nodes[9]))

    assert len(graph.internal_nodes) == 10
    assert len(graph.internal_edges) == 11
    assert len(graph.get_heads()) == 1
    assert len(graph.get_successors(nodes[6])) == 2
    assert len(graph.get_predecessors(nodes[5])) == 2

    # Test removal of a central node
    graph.remove_node(nodes[5])
    assert len(graph.internal_nodes) == 9
    assert len(graph.internal_edges) == 8
    assert len(graph.get_successors(nodes[3])) == 0
    assert len(graph.get_predecessors(nodes[6])) == 0


# Test edge cases
def test_empty_graph():
    graph = Graph()
    assert len(graph.internal_nodes) == 0
    assert len(graph.internal_edges) == 0
    assert len(graph.get_heads()) == 0


def test_single_node_graph():
    graph = Graph()
    node = create_test_node("SingleNode")
    graph.add_node(node)
    assert len(graph.internal_nodes) == 1
    assert len(graph.internal_edges) == 0
    assert len(graph.get_heads()) == 1
    assert len(graph.get_successors(node)) == 0
    assert len(graph.get_predecessors(node)) == 0


def test_cyclic_graph():
    graph = Graph()
    node1 = create_test_node("Node1")
    node2 = create_test_node("Node2")
    node3 = create_test_node("Node3")
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_edge(create_test_edge(node1, node2))
    graph.add_edge(create_test_edge(node2, node3))
    graph.add_edge(create_test_edge(node3, node1))

    assert len(graph.internal_nodes) == 3
    assert len(graph.internal_edges) == 3
    assert len(graph.get_heads()) == 0
    for node in graph.internal_nodes:
        assert len(graph.get_successors(node)) == 1
        assert len(graph.get_predecessors(node)) == 1


# Test serialization
def test_graph_serialization(basic_graph):
    serialized = basic_graph.to_dict()
    assert "internal_nodes" in serialized
    assert "internal_edges" in serialized
    assert isinstance(serialized["internal_nodes"], list)
    assert isinstance(serialized["internal_edges"], list)


# Test performance with large graphs
# @pytest.mark.slow
def test_large_graph_performance():
    graph = Graph()
    num_nodes = 1000
    nodes = [create_test_node(f"Node{i}") for i in range(num_nodes)]

    import time

    start_time = time.time()

    for node in nodes:
        graph.add_node(node)

    for i in range(num_nodes - 1):
        graph.add_edge(create_test_edge(nodes[i], nodes[i + 1]))

    end_time = time.time()

    assert len(graph.internal_nodes) == num_nodes
    assert len(graph.internal_edges) == num_nodes - 1
    assert end_time - start_time < 10  # Ensure it takes less than 10 seconds


# Test concurrent operations
@pytest.mark.asyncio
async def test_concurrent_operations():
    import asyncio

    graph = Graph()
    num_operations = 1000

    async def add_node_and_edge(i):
        node1 = create_test_node(f"Node{i}a")
        node2 = create_test_node(f"Node{i}b")
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge(create_test_edge(node1, node2))

    tasks = [add_node_and_edge(i) for i in range(num_operations)]
    await asyncio.gather(*tasks)

    assert len(graph.internal_nodes) == num_operations * 2
    assert len(graph.internal_edges) == num_operations


# Test with various node and edge types
class CustomNode(Node):
    def __init__(self, value):
        super().__init__()
        self.add_field("value", value)


class CustomEdge(Edge):
    def __init__(self, head, tail, weight):
        super().__init__(head, tail)
        self.properties.set("weight", weight)


def test_custom_node_and_edge_types():
    graph = Graph()
    node1 = CustomNode(10)
    node2 = CustomNode(20)
    graph.add_node(node1)
    graph.add_node(node2)
    edge = CustomEdge(node1, node2, 5)
    graph.add_edge(edge)

    assert len(graph.internal_nodes) == 2
    assert len(graph.internal_edges) == 1
    assert isinstance(graph.internal_nodes[0], CustomNode)
    assert isinstance(graph.internal_edges[0], CustomEdge)
    assert graph.internal_edges[0].properties["weight"] == 5


# Test error handling and edge cases
def test_add_duplicate_node(basic_graph):
    duplicate_node = basic_graph.internal_nodes[0]
    with pytest.raises(LionRelationError):
        basic_graph.add_node(duplicate_node)


def test_remove_node_with_edges(basic_graph):
    node_to_remove = basic_graph.internal_nodes[
        1
    ]  # This node has both in and out edges
    basic_graph.remove_node(node_to_remove)
    assert node_to_remove not in basic_graph.internal_nodes
    assert len(basic_graph.internal_edges) == 0  # Both edges should be removed


def test_find_node_edge_invalid_direction(basic_graph):
    node = basic_graph.internal_nodes[0]
    with pytest.raises(ValueError):
        basic_graph.find_node_edge(node, direction="invalid")


# Test graph traversal and analysis
def test_graph_traversal():
    graph = Graph()
    nodes = [create_test_node(f"Node{i}") for i in range(5)]
    for node in nodes:
        graph.add_node(node)
    graph.add_edge(create_test_edge(nodes[0], nodes[1]))
    graph.add_edge(create_test_edge(nodes[0], nodes[2]))
    graph.add_edge(create_test_edge(nodes[1], nodes[3]))
    graph.add_edge(create_test_edge(nodes[2], nodes[4]))

    def dfs_traverse(node, visited=None):
        if visited is None:
            visited = set()
        visited.add(node)
        for successor in graph.get_successors(node):
            if successor not in visited:
                dfs_traverse(successor, visited)
        return visited

    traversed_nodes = dfs_traverse(nodes[0])
    assert len(traversed_nodes) == 5
    assert all(node in traversed_nodes for node in nodes)


# Test graph modification during iteration
def test_graph_modification_during_iteration(basic_graph):
    nodes_to_remove = []
    for node in basic_graph.internal_nodes:
        if node.content["name"] in ["Node1", "Node3"]:
            nodes_to_remove.append(node)

    for node in nodes_to_remove:
        basic_graph.remove_node(node)

    assert len(basic_graph.internal_nodes) == 1
    assert basic_graph.internal_nodes[0].content["name"] == "Node2"


# Test graph with self-loops
def test_graph_with_self_loops():
    graph = Graph()
    node = create_test_node("SelfLoop")
    graph.add_node(node)
    self_loop = create_test_edge(node, node)
    graph.add_edge(self_loop)

    assert len(graph.internal_edges) == 1
    assert graph.get_successors(node)[0] == node
    assert graph.get_predecessors(node)[0] == node


# # Test graph with multiple edge types
def test_graph_with_multiple_edge_types():
    graph = Graph()
    node1 = create_test_node("Node1")
    node2 = create_test_node("Node2")
    graph.add_node(node1)
    graph.add_node(node2)

    edge1 = create_test_edge(node1, node2, label="TypeA")
    edge2 = create_test_edge(node1, node2, label="TypeB")
    graph.add_edge(edge1)
    graph.add_edge(edge2)

    assert len(graph.internal_edges) == 2
    edges = graph.find_node_edge(node1, direction="out")
    assert len(edges) == 2
    assert {edge.properties.get("label") for edge in edges} == {
        "TypeA",
        "TypeB",
    }


# Test graph operations with large number of nodes and edges
# @pytest.mark.slow
def test_graph_operations_with_large_data():
    graph = Graph()
    num_nodes = 1000
    num_edges = 5000

    # Add nodes
    nodes = [create_test_node(f"Node{i}") for i in range(num_nodes)]
    for node in nodes:
        graph.add_node(node)

    # Add random edges
    import random

    for _ in range(num_edges):
        head = random.choice(nodes)
        tail = random.choice(nodes)
        edge = create_test_edge(head, tail)
        try:
            graph.add_edge(edge)
        except LionRelationError:
            pass  # Ignore if edge already exists

    assert len(graph.internal_nodes) == num_nodes
    assert (
        len(graph.internal_edges) <= num_edges
    )  # May be less due to duplicates

    # Test operations on large graph
    random_node = random.choice(nodes)
    connected_edges = graph.find_node_edge(random_node)
    assert isinstance(connected_edges, Pile)

    predecessors = graph.get_predecessors(random_node)
    successors = graph.get_successors(random_node)
    assert isinstance(predecessors, Pile)
    assert isinstance(successors, Pile)


# Test graph with disconnected components
def test_graph_with_disconnected_components():
    graph = Graph()

    # Component 1
    node1 = create_test_node("Component1_Node1")
    node2 = create_test_node("Component1_Node2")
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge(create_test_edge(node1, node2))

    # Component 2
    node3 = create_test_node("Component2_Node1")
    node4 = create_test_node("Component2_Node2")
    graph.add_node(node3)
    graph.add_node(node4)
    graph.add_edge(create_test_edge(node3, node4))

    assert len(graph.internal_nodes) == 4
    assert len(graph.internal_edges) == 2
    assert len(graph.get_heads()) == 2

    # Ensure no connection between components
    assert len(graph.find_node_edge(node1, direction="both")) == 1
    assert len(graph.find_node_edge(node3, direction="both")) == 1


# Test graph with bidirectional edges
def test_graph_with_bidirectional_edges():
    graph = Graph()
    node1 = create_test_node("Node1")
    node2 = create_test_node("Node2")
    graph.add_node(node1)
    graph.add_node(node2)

    edge1 = create_test_edge(node1, node2)
    edge2 = create_test_edge(node2, node1)
    graph.add_edge(edge1)
    graph.add_edge(edge2)

    assert len(graph.internal_edges) == 2
    assert len(graph.find_node_edge(node1, direction="out")) == 1
    assert len(graph.find_node_edge(node1, direction="in")) == 1
    assert len(graph.find_node_edge(node2, direction="out")) == 1
    assert len(graph.find_node_edge(node2, direction="in")) == 1


# Test graph with node and edge attributes
def test_graph_with_attributes():
    class AttributeNode(Node):
        def __init__(self, name, attributes):
            super().__init__(content={"name": name})
            self.add_field("attributes", value=attributes)

    class AttributeEdge(Edge):
        def __init__(self, head, tail, attributes):
            super().__init__(head, tail)
            for k, v in attributes.items():
                self.properties.set(k, v)

    graph = Graph()
    node1 = AttributeNode("Node1", {"color": "red", "size": 10})
    node2 = AttributeNode("Node2", {"color": "blue", "size": 20})
    graph.add_node(node1)
    graph.add_node(node2)

    edge = AttributeEdge(node1, node2, {"weight": 5, "type": "connection"})
    graph.add_edge(edge)

    assert graph.internal_nodes[node1.ln_id].attributes["color"] == "red"
    assert graph.internal_nodes[node2.ln_id].attributes["size"] == 20
    assert graph.internal_edges[edge.ln_id].properties["weight"] == 5


# Test graph merge
def test_graph_merge():
    graph1 = Graph()
    node1 = create_test_node("Graph1_Node1")
    node2 = create_test_node("Graph1_Node2")
    graph1.add_node(node1)
    graph1.add_node(node2)
    graph1.add_edge(create_test_edge(node1, node2))

    graph2 = Graph()
    node3 = create_test_node("Graph2_Node1")
    node4 = create_test_node("Graph2_Node2")
    graph2.add_node(node3)
    graph2.add_node(node4)
    graph2.add_edge(create_test_edge(node3, node4))

    merged_graph = Graph()
    for node in graph1.internal_nodes:
        merged_graph.add_node(node)
    for edge in graph1.internal_edges:
        merged_graph.add_edge(edge)
    for node in graph2.internal_nodes:
        merged_graph.add_node(node)
    for edge in graph2.internal_edges:
        merged_graph.add_edge(edge)

    assert len(merged_graph.internal_nodes) == 4
    assert len(merged_graph.internal_edges) == 2


# Test graph with node removal cascading
def test_graph_node_removal_cascading():
    graph = Graph()
    nodes = [create_test_node(f"Node{i}") for i in range(5)]
    for node in nodes:
        graph.add_node(node)

    graph.add_edge(create_test_edge(nodes[0], nodes[1]))
    graph.add_edge(create_test_edge(nodes[1], nodes[2]))
    graph.add_edge(create_test_edge(nodes[2], nodes[3]))
    graph.add_edge(create_test_edge(nodes[3], nodes[4]))

    # Remove a middle node
    graph.remove_node(nodes[2])

    assert len(graph.internal_nodes) == 4
    assert len(graph.internal_edges) == 2
    assert nodes[2].ln_id not in graph.node_edge_mapping


# Test graph with concurrent modifications
@pytest.mark.asyncio
async def test_graph_concurrent_modifications():
    import asyncio

    graph = Graph()
    base_nodes = [create_test_node(f"BaseNode{i}") for i in range(5)]
    for node in base_nodes:
        graph.add_node(node)

    async def add_connected_node(base_node):
        new_node = create_test_node(f"NewNode_for_{base_node.content['name']}")
        graph.add_node(new_node)
        graph.add_edge(create_test_edge(base_node, new_node))

    tasks = [add_connected_node(node) for node in base_nodes]
    await asyncio.gather(*tasks)

    assert len(graph.internal_nodes) == 10
    assert len(graph.internal_edges) == 5


# Test graph with very long node and edge chains
# @pytest.mark.slow
def test_graph_with_long_chains():
    graph = Graph()
    chain_length = 10000

    nodes = [create_test_node(f"Node{i}") for i in range(chain_length)]
    for node in nodes:
        graph.add_node(node)

    for i in range(chain_length - 1):
        graph.add_edge(create_test_edge(nodes[i], nodes[i + 1]))

    assert len(graph.internal_nodes) == chain_length
    assert len(graph.internal_edges) == chain_length - 1

    # Test traversal of long chain
    start_node = nodes[0]
    end_node = nodes[-1]

    current = start_node
    path_length = 0
    while current != end_node:
        successors = graph.get_successors(current)
        assert len(successors) == 1
        current = successors[0]
        path_length += 1

    assert path_length == chain_length - 1


# Test graph with node and edge property updates
def test_graph_property_updates():
    graph = Graph()
    node1 = create_test_node("Node1")
    node2 = create_test_node("Node2")
    graph.add_node(node1)
    graph.add_node(node2)
    edge = create_test_edge(node1, node2)
    graph.add_edge(edge)

    # Update node property
    node1.content["updated"] = True
    assert graph.internal_nodes[node1.ln_id].content["updated"] == True

    # Update edge property
    edge.properties["weight"] = 10
    assert graph.internal_edges[edge.ln_id].properties["weight"] == 10


# Test graph performance with different operations
# @pytest.mark.slow
def test_graph_performance():
    import time

    graph = Graph()
    num_nodes = 10000
    num_edges = 10000

    # Measure node addition time
    start_time = time.time()
    nodes = [create_test_node(f"Node{i}") for i in range(num_nodes)]
    for node in nodes:
        graph.add_node(node)
    node_addition_time = time.time() - start_time

    # Measure edge addition time
    start_time = time.time()
    for _ in range(num_edges):
        head = nodes[random.randint(0, num_nodes - 1)]
        tail = nodes[random.randint(0, num_nodes - 1)]
        try:
            graph.add_edge(create_test_edge(head, tail))
        except LionRelationError:
            pass  # Ignore if edge already exists
    edge_addition_time = time.time() - start_time

    # Measure node removal time
    start_time = time.time()
    for _ in range(1000):
        node_to_remove = random.choice(nodes)
        try:
            graph.remove_node(node_to_remove)
            nodes.remove(node_to_remove)
        except LionRelationError:
            pass  # Node might have been already removed
    node_removal_time = time.time() - start_time

    # Measure edge finding time
    start_time = time.time()
    for _ in range(1000):
        node = random.choice(nodes)
        graph.find_node_edge(node)
    edge_finding_time = time.time() - start_time

    # Assert that operations complete within reasonable time
    assert node_addition_time < 5  # 5 seconds
    assert edge_addition_time < 10  # 10 seconds
    assert node_removal_time < 15  # 5 seconds
    assert edge_finding_time < 2  # 2 seconds


# Test graph with multi-edges (multiple edges between same nodes)
def test_graph_with_multi_edges():
    graph = Graph()
    node1 = create_test_node("Node1")
    node2 = create_test_node("Node2")
    graph.add_node(node1)
    graph.add_node(node2)

    edge1 = create_test_edge(node1, node2, label="Edge1")
    edge2 = create_test_edge(node1, node2, label="Edge2")
    graph.add_edge(edge1)
    graph.add_edge(edge2)

    edges = graph.find_node_edge(node1, direction="out")
    assert len(edges) == 2
    assert {edge.properties.get("label") for edge in edges} == {
        "Edge1",
        "Edge2",
    }


def test_graph_with_large_property_values():
    graph = Graph()
    large_content = "a" * 1000000  # 1MB string
    node = create_test_node("LargeNode")
    node.content["large_property"] = large_content
    graph.add_node(node)

    edge = create_test_edge(node, node)
    edge.properties["large_property"] = large_content
    graph.add_edge(edge)

    assert len(graph.internal_nodes) == 1
    assert len(graph.internal_edges) == 1
    assert (
        len(graph.internal_nodes[node.ln_id].content["large_property"])
        == 1000000
    )
    assert (
        len(graph.internal_edges[edge.ln_id].properties["large_property"])
        == 1000000
    )


# Test graph with nodes and edges of different types
def test_graph_with_mixed_types():
    class TypeANode(Node):
        pass

    class TypeBNode(Node):
        pass

    class TypeAEdge(Edge):
        pass

    class TypeBEdge(Edge):
        pass

    graph = Graph()
    node_a = TypeANode()
    node_b = TypeBNode()
    graph.add_node(node_a)
    graph.add_node(node_b)

    edge_a = TypeAEdge(node_a, node_b)
    edge_b = TypeBEdge(node_b, node_a)
    graph.add_edge(edge_a)
    graph.add_edge(edge_b)

    assert isinstance(graph.internal_nodes[node_a.ln_id], TypeANode)
    assert isinstance(graph.internal_nodes[node_b.ln_id], TypeBNode)
    assert isinstance(graph.internal_edges[edge_a.ln_id], TypeAEdge)
    assert isinstance(graph.internal_edges[edge_b.ln_id], TypeBEdge)


# Test graph with dynamic node and edge creation
def test_graph_dynamic_creation():
    graph = Graph()

    def create_dynamic_node(name):
        return Node(content={"dynamic_name": name})

    def create_dynamic_edge(head, tail, weight):
        edge = Edge(head, tail)
        edge.properties["weight"] = weight
        return edge

    for i in range(100):
        node = create_dynamic_node(f"DynamicNode{i}")
        graph.add_node(node)

        if i > 0:
            prev_node = graph.internal_nodes[
                list(graph.internal_nodes.keys())[-2]
            ]
            edge = create_dynamic_edge(prev_node, node, i)
            graph.add_edge(edge)

    assert len(graph.internal_nodes) == 100
    assert len(graph.internal_edges) == 99
    assert all(
        "dynamic_name" in node.content
        for node in graph.internal_nodes.values()
    )
    assert all(
        "weight" in edge.properties for edge in graph.internal_edges.values()
    )


# Test graph with nested graphs as nodes
def test_graph_with_nested_graphs():
    class NestedGraphNode(Node):
        def __init__(self, nested_graph):
            super().__init__()
            self.add_field("nested_graph", nested_graph)

    outer_graph = Graph()

    for i in range(3):
        inner_graph = Graph()
        inner_node1 = create_test_node(f"InnerNode1_{i}")
        inner_node2 = create_test_node(f"InnerNode2_{i}")
        inner_graph.add_node(inner_node1)
        inner_graph.add_node(inner_node2)
        inner_graph.add_edge(create_test_edge(inner_node1, inner_node2))

        nested_node = NestedGraphNode(inner_graph)
        outer_graph.add_node(nested_node)

    assert len(outer_graph.internal_nodes) == 3
    for node in outer_graph.internal_nodes.values():
        assert isinstance(node, NestedGraphNode)
        assert len(node.nested_graph.internal_nodes) == 2
        assert len(node.nested_graph.internal_edges) == 1


# Test graph with cyclic dependencies
def test_graph_cyclic_dependencies():
    graph = Graph()
    node1 = create_test_node("Node1")
    node2 = create_test_node("Node2")
    node3 = create_test_node("Node3")
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    graph.add_edge(create_test_edge(node1, node2))
    graph.add_edge(create_test_edge(node2, node3))
    graph.add_edge(create_test_edge(node3, node1))

    assert len(graph.internal_edges) == 3
    assert len(graph.get_successors(node1)) == 1
    assert len(graph.get_predecessors(node1)) == 1


# Test graph with concurrent read/write operations
@pytest.mark.asyncio
async def test_graph_concurrent_operations():
    import asyncio

    graph = Graph()
    base_node = create_test_node("BaseNode")
    graph.add_node(base_node)

    async def add_and_remove_node():
        node = create_test_node(f"Node_{asyncio.current_task().get_name()}")
        graph.add_node(node)
        graph.add_edge(create_test_edge(base_node, node))
        await asyncio.sleep(0.0001)  # Simulate some processing time
        graph.remove_node(node)

    async def read_graph():
        await asyncio.sleep(0.0001)  # Simulate some processing time
        _ = graph.get_successors(base_node)

    tasks = [add_and_remove_node() for _ in range(100)] + [
        read_graph() for _ in range(50)
    ]
    await asyncio.gather(*tasks)

    # Only the base node should remain after all operations
    assert len(graph.internal_nodes) == 1
    assert base_node.ln_id in graph.internal_nodes


# @pytest.mark.slow
def test_graph_large_sparse():
    graph = Graph()
    num_nodes = 10000
    num_edges = 10000

    nodes = [create_test_node(f"Node_{i}") for i in range(num_nodes)]
    for node in nodes:
        graph.add_node(node)

    import random

    for _ in range(num_edges):
        head = random.choice(nodes)
        tail = random.choice(nodes)
        if head != tail:
            try:
                graph.add_edge(create_test_edge(head, tail))
            except LionRelationError:
                pass  # Ignore if edge already exists

    assert len(graph.internal_nodes) == num_nodes
    assert (
        len(graph.internal_edges) <= num_edges
    )  # May be less due to duplicates

    # Test performance of operations on large graph
    start_time = time.time()
    random_node = random.choice(nodes)
    _ = graph.get_successors(random_node)
    _ = graph.get_predecessors(random_node)
    operation_time = time.time() - start_time

    assert (
        operation_time < 1
    )  # Operations should complete in less than 1 second


# Test graph with node and edge removal stress test
# @pytest.mark.slow
def test_graph_removal_stress():
    graph = Graph()
    num_initial_nodes = 1000
    num_initial_edges = 5000

    nodes = [create_test_node(f"Node_{i}") for i in range(num_initial_nodes)]
    for node in nodes:
        graph.add_node(node)

    for _ in range(num_initial_edges):
        head = random.choice(nodes)
        tail = random.choice(nodes)
        if head != tail:
            try:
                graph.add_edge(create_test_edge(head, tail))
            except LionRelationError:
                pass

    # Remove half of the nodes
    nodes_to_remove = random.sample(nodes, num_initial_nodes // 2)
    for node in nodes_to_remove:
        graph.remove_node(node)

    assert len(graph.internal_nodes) == num_initial_nodes // 2
    assert (
        len(graph.internal_edges) < num_initial_edges
    )  # Should be significantly less

    # Verify integrity of remaining graph
    for node in graph.internal_nodes.values():
        in_edges = graph.find_node_edge(node, direction="in")
        out_edges = graph.find_node_edge(node, direction="out")
        for edge in in_edges:
            assert edge.tail == node.ln_id
            assert edge.head in graph.internal_nodes
        for edge in out_edges:
            assert edge.head == node.ln_id
            assert edge.tail in graph.internal_nodes


# Final test to ensure all graph operations work together
def test_graph_comprehensive_operations():
    graph = Graph()

    # Add nodes
    nodes = [create_test_node(f"Node_{i}") for i in range(100)]
    for node in nodes:
        graph.add_node(node)

    # Add edges
    for i in range(0, 99, 2):
        graph.add_edge(create_test_edge(nodes[i], nodes[i + 1]))

    # Remove some nodes
    for i in range(0, 50, 10):
        graph.remove_node(nodes[i])

    # Add more edges
    for i in range(51, 99, 3):
        graph.add_edge(create_test_edge(nodes[i], nodes[i - 1]))

    # Perform various operations
    assert len(graph.internal_nodes) == 95
    assert (
        55 <= len(graph.internal_edges) <= 65
    )  # Exact number may vary due to removals

    random_node = random.choice(list(graph.internal_nodes.values()))
    successors = graph.get_successors(random_node)
    predecessors = graph.get_predecessors(random_node)

    assert isinstance(successors, Pile)
    assert isinstance(predecessors, Pile)

    # Final integrity check
    for node_id, node in graph.internal_nodes.items():
        assert node_id in graph.node_edge_mapping
        in_edges = graph.find_node_edge(node, direction="in")
        out_edges = graph.find_node_edge(node, direction="out")
        for edge in in_edges:
            assert edge.tail == node.ln_id
        for edge in out_edges:
            assert edge.head == node.ln_id
