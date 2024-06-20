import unittest
from lionagi.os.collections.abc import LionTypeError, ItemNotFoundError
from lionagi.os.collections.graph.graph import Graph
from lionagi.os.collections.node.node import Node
from lionagi.os.collections.edge.edge import Edge
from lionagi.os.lib.data_handlers import to_list


class TestGraph(unittest.TestCase):

    def setUp(self):
        """Set up a basic graph for testing."""
        self.node1 = Node()
        self.node2 = Node()
        self.node3 = Node()
        self.node4 = Node()
        self.g = Graph()

    def test_initial_size(self):
        """Test the initial size of the graph."""
        self.assertEqual(self.g.size(), 0)

    def test_initial_internal_edges(self):
        """Test the initial number of internal edges."""
        self.assertEqual(len(self.g.internal_edges), 0)

    def test_add_node_no_edge(self):
        """Test that adding nodes does not create any edges."""
        self.g.add_node([self.node1, self.node2, self.node3, self.node4])
        self.assertEqual(len(self.g.internal_edges), 0)

    def test_add_edges(self):
        """Test adding edges between nodes."""
        self.g.add_edge(self.node1, self.node2)
        self.g.add_edge(self.node2, self.node3)
        self.g.add_edge(self.node3, self.node4)
        self.assertEqual(len(self.g.internal_edges), 3)

    def test_get_node(self):
        """Test retrieving a node by its identifier."""
        self.g.add_node(self.node2)
        node5 = self.g.get_node(self.node2)
        self.assertEqual(node5, self.node2)

    def test_get_node_edges(self):
        """Test getting the edges of a node."""
        self.g.add_edge(self.node1, self.node2)
        self.assertEqual(len(self.g.get_node_edges(self.node1)), 1)

    def test_get_heads(self):
        """Test getting head nodes."""
        self.g.add_edge(self.node1, self.node2)
        self.g.add_edge(self.node2, self.node3)
        self.g.add_edge(self.node3, self.node4)
        self.assertEqual(len(self.g.get_heads()), 1)

    def test_is_acyclic(self):
        """Test if the graph is acyclic."""
        self.g.add_edge(self.node1, self.node2)
        self.g.add_edge(self.node2, self.node3)
        self.g.add_edge(self.node3, self.node4)
        self.assertTrue(self.g.is_acyclic())

    def test_remove_edge(self):
        """Test removing an edge from the graph."""
        self.g.add_edge(self.node1, self.node2)
        self.g.add_edge(self.node2, self.node3)
        self.g.add_edge(self.node3, self.node4)
        edge = self.g.internal_edges[0]
        self.g.remove_edge(edge)
        self.assertEqual(len(self.g.internal_edges), 2)

    def test_remove_nonexistent_edge(self):
        """Test removing a nonexistent edge."""
        self.g.add_edge(self.node1, self.node2)
        with self.assertRaises(ItemNotFoundError):
            self.g.remove_edge(edge=Edge(head=self.node2, tail=self.node3))

    def test_clear(self):
        """Test clearing all nodes and edges from the graph."""
        self.g.add_node([self.node1, self.node2, self.node3, self.node4])
        self.g.add_edge(self.node1, self.node2)
        self.g.add_edge(self.node2, self.node3)
        self.g.add_edge(self.node3, self.node4)
        self.g.clear()
        self.assertTrue(self.g.is_empty())
        self.assertEqual(len(self.g.internal_edges), 0)

    def test_display(self):
        """Test displaying the graph (visual check)."""
        self.g.add_edge(self.node1, self.node2)
        self.g.add_edge(self.node2, self.node3)
        self.g.add_edge(self.node3, self.node4)
        self.g.display()  # This should display the graph visually


if __name__ == "__main__":
    unittest.main()
