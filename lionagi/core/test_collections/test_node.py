import unittest
from lionagi.os.collections.node.node import Node
from lionagi.os.collections.abc import RelationError, Condition
from lionagi.os.collections.edge.edge import Edge


class TestNode(unittest.TestCase):

    def setUp(self):
        """Setup nodes for testing."""
        self.node_a = Node()
        self.node_b = Node()
        self.node_c = Node()

    def test_initialization(self):
        """Test that a Node initializes with empty relations."""
        self.assertEqual(len(self.node_a.relations["in"]), 0)
        self.assertEqual(len(self.node_a.relations["out"]), 0)

    def test_relate_outgoing(self):
        """Test relating nodes with an outgoing edge."""
        self.node_a.relate(self.node_b, "out")
        self.assertIn(self.node_b.ln_id, self.node_a.related_nodes)
        self.assertIn(self.node_a.ln_id, self.node_b.related_nodes)
        self.assertIn(self.node_b.ln_id, self.node_a.successors)
        self.assertIn(self.node_a.ln_id, self.node_b.predecessors)

    def test_relate_incoming(self):
        """Test relating nodes with an incoming edge."""
        self.node_a.relate(self.node_c, "in")
        self.assertIn(self.node_c.ln_id, self.node_a.related_nodes)
        self.assertIn(self.node_a.ln_id, self.node_c.related_nodes)
        self.assertIn(self.node_a.ln_id, self.node_c.successors)
        self.assertIn(self.node_c.ln_id, self.node_a.predecessors)

    def test_invalid_relate(self):
        """Test that relating nodes with an invalid direction raises ValueError."""
        with self.assertRaises(ValueError):
            self.node_a.relate(self.node_b, "invalid_direction")

    def test_remove_edge(self):
        """Test removing a specific edge between nodes."""
        self.node_a.relate(self.node_b, "out")
        edge = next(iter(self.node_a.relations["out"]))
        self.assertTrue(self.node_a.remove_edge(self.node_b, edge))

    def test_unrelate_all_edges(self):
        """Test unrelating all edges between nodes."""
        self.node_a.relate(self.node_b, "out")
        self.assertTrue(self.node_a.unrelate(self.node_b))
        self.assertNotIn(self.node_b.ln_id, self.node_a.related_nodes)
        self.assertNotIn(self.node_a.ln_id, self.node_b.related_nodes)

    def test_unrelate_specific_edge(self):
        """Test unrelating a specific edge between nodes."""
        self.node_a.relate(self.node_b, "out")
        edge = next(iter(self.node_a.relations["out"]))
        self.assertTrue(self.node_a.unrelate(self.node_b, edge))
        self.assertNotIn(self.node_b.ln_id, self.node_a.related_nodes)
        self.assertNotIn(self.node_a.ln_id, self.node_b.related_nodes)

    def test_node_relations(self):
        """Test that node relations are correctly categorized."""
        self.node_a.relate(self.node_b, "out")
        self.node_a.relate(self.node_c, "in")
        relations = self.node_a.node_relations
        self.assertIn(self.node_b.ln_id, relations["out"])
        self.assertIn(self.node_c.ln_id, relations["in"])

    def test_related_nodes(self):
        """Test that related nodes list is correct."""
        self.node_a.relate(self.node_b, "out")
        self.node_a.relate(self.node_c, "in")
        related_nodes = self.node_a.related_nodes
        self.assertIn(self.node_b.ln_id, related_nodes)
        self.assertIn(self.node_c.ln_id, related_nodes)

    def test_predecessors(self):
        """Test that predecessors list is correct."""
        self.node_a.relate(self.node_c, "in")
        self.assertIn(self.node_c.ln_id, self.node_a.predecessors)

    def test_successors(self):
        """Test that successors list is correct."""
        self.node_a.relate(self.node_b, "out")
        self.assertIn(self.node_b.ln_id, self.node_a.successors)

    def test_str(self):
        """Test the string representation of a node."""
        self.node_a.relate(self.node_b, "out")
        node_str = str(self.node_a)
        self.assertIn(self.node_a.ln_id, node_str)
        self.assertIn("relations", node_str)
        self.assertIn("1", node_str)  # 1 relation

    def test_repr(self):
        """Test the repr representation of a node."""
        self.node_a.relate(self.node_b, "out")
        node_repr = repr(self.node_a)
        self.assertIn(self.node_a.ln_id, node_repr)
        self.assertIn("relations", node_repr)
        self.assertIn("1", node_repr)  # 1 relation


if __name__ == "__main__":
    unittest.main()
