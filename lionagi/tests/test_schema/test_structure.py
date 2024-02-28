from lionagi.core.schema.structure import *
import unittest
from unittest.mock import patch


class TestRelationship(unittest.TestCase):

    def setUp(self):
        self.relationship = Relationship(source_node_id="node1", target_node_id="node2")

    def test_initial_attributes(self):
        """Test initial attributes are set correctly."""
        self.assertEqual(self.relationship.source_node_id, "node1")
        self.assertEqual(self.relationship.target_node_id, "node2")
        self.assertEqual(self.relationship.condition, {})

    def test_add_condition(self):
        """Test adding a condition to the relationship."""
        self.relationship.add_condition({"key": "value"})
        self.assertIn("key", self.relationship.condition)
        self.assertEqual(self.relationship.condition["key"], "value")

    def test_remove_condition_existing_key(self):
        """Test removing a condition from existing relationship."""
        self.relationship.add_condition({"key": "value"})
        removed_value = self.relationship.remove_condition("key")
        self.assertEqual(removed_value, "value")
        self.assertNotIn("key", self.relationship.condition)

    def test_remove_condition_non_existing_key(self):
        """Test removing a condition from non-existing relationship."""
        with self.assertRaises(KeyError):
            self.relationship.remove_condition("non_existing_key")

    def test_condition_exists_true(self):
        """Test checking if a condition exists."""
        self.relationship.add_condition({"key": "value"})
        self.assertTrue(self.relationship.condition_exists("key"))

    def test_condition_exists_false(self):
        """Test checking if a condition exists."""
        self.assertFalse(self.relationship.condition_exists("non_existing_key"))

    def test_get_condition_specific_key(self):
        """Test retrieving a specific condition."""
        self.relationship.add_condition({"key": "value"})
        condition_value = self.relationship.get_condition("key")
        self.assertEqual(condition_value, "value")

    def test_get_condition_all(self):
        """Test retrieving all conditions."""
        self.relationship.add_condition({"key": "value"})
        conditions = self.relationship.get_condition()
        self.assertEqual(conditions, {"key": "value"})

    def test_get_condition_non_existing_key(self):
        """Test that getting a non-existent condition raises ValueError."""
        with self.assertRaises(ValueError):
            self.relationship.get_condition("non_existing_key")

    def test_str_representation(self):
        """Test the string representation of the relationship."""
        str_repr = str(self.relationship)
        self.assertIsInstance(str_repr, str)
        self.assertIn("node1", str_repr)
        self.assertIn("node2", str_repr)

    def test_repr_representation(self):
        """Test the detailed string representation of the relationship."""
        repr_str = repr(self.relationship)
        self.assertIsInstance(repr_str, str)
        self.assertIn("node1", repr_str)
        self.assertIn("node2", repr_str)


class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
        self.node1 = BaseNode(id_='node1')
        self.node2 = BaseNode(id_='node2')
        self.relationship = Relationship(id_='rel1', source_node_id='node1',
                                         target_node_id='node2')

    def test_add_and_check_node(self):
        """Test adding a node and checking its existence."""
        self.graph.add_node(self.node1)
        self.assertTrue(self.graph.node_exist(self.node1))

    def test_add_and_check_relationship(self):
        """Test adding a relationship and checking its existence."""
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_relationship(self.relationship)
        self.assertTrue(self.graph.relationship_exist(self.relationship))

    def test_remove_node(self):
        """Test removing a node and its related data."""
        self.graph.add_node(self.node1)
        self.graph.remove_node(self.node1)
        self.assertFalse(self.graph.node_exist(self.node1))

    def test_remove_relationship(self):
        """Test removing a relationship."""
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_relationship(self.relationship)
        self.graph.remove_relationship(self.relationship)
        self.assertFalse(self.graph.relationship_exist(self.relationship))

    def test_get_node_relationships(self):
        """Test retrieving relationships of a node."""
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_relationship(self.relationship)
        relationships = self.graph.get_node_relationships(self.node1, out_edge=True)
        self.assertIn(self.relationship, relationships)

    def test_graph_empty(self):
        """Test checking if the graph is empty."""
        self.assertTrue(self.graph.is_empty())
        self.graph.add_node(self.node1)
        self.assertFalse(self.graph.is_empty())

    def test_clear_graph(self):
        """Test clearing the graph."""
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_relationship(self.relationship)
        self.graph.clear()
        self.assertTrue(self.graph.is_empty())

    # @patch('networkx.DiGraph')
    # def test_to_networkx(self, mock_DiGraph):
    #     """Test converting the graph to a NetworkX graph object."""
    #     self.graph.to_networkx()
    #     mock_DiGraph.assert_called()


class TestStructure(unittest.TestCase):

    def setUp(self):
        self.structure = Structure()
        self.node1 = BaseNode(id_='node1')
        self.node2 = BaseNode(id_='node2')
        self.relationship = Relationship(id_='rel1', source_node_id='node1',
                                         target_node_id='node2')

    def test_add_and_check_node(self):
        """Test adding a node and checking its existence."""
        self.structure.add_node(self.node1)
        self.assertTrue(self.structure.node_exist(self.node1))

    def test_add_and_check_relationship(self):
        """Test adding a relationship and checking its existence."""
        self.structure.add_node(self.node1)
        self.structure.add_node(self.node2)
        self.structure.add_relationship(self.relationship)
        self.assertTrue(self.structure.relationship_exist(self.relationship))

    def test_remove_node(self):
        """Test removing a node and its associated data."""
        self.structure.add_node(self.node1)
        removed_node = self.structure.remove_node(self.node1)
        self.assertFalse(self.structure.node_exist(self.node1))
        self.assertEqual(removed_node.id_, self.node1.id_)

    def test_remove_relationship(self):
        """Test removing a relationship."""
        self.structure.add_node(self.node1)
        self.structure.add_node(self.node2)
        self.structure.add_relationship(self.relationship)
        removed_relationship = self.structure.remove_relationship(self.relationship)
        self.assertFalse(self.structure.relationship_exist(self.relationship))
        self.assertEqual(removed_relationship.id_, self.relationship.id_)

    def test_get_node_relationships(self):
        """Test retrieving relationships of a specific node."""
        self.structure.add_node(self.node1)
        self.structure.add_node(self.node2)
        self.structure.add_relationship(self.relationship)
        relationships = self.structure.get_node_relationships(self.node1, out_edge=True)
        self.assertIn(self.relationship, relationships)

    def test_graph_empty(self):
        """Test checking if the structure is empty."""
        self.assertTrue(self.structure.is_empty())
        self.structure.add_node(self.node1)
        self.assertFalse(self.structure.is_empty())

    def test_filter_relationships_by_label(self):
        """Test filtering relationships by label."""
        self.relationship.label = "test_label"
        self.structure.add_node(self.node1)
        self.structure.add_node(self.node2)
        self.structure.add_relationship(self.relationship)
        filtered_relationships = self.structure.get_node_relationships(self.node1, labels="test_label")
        self.assertEqual(len(filtered_relationships), 1)
        self.assertEqual(filtered_relationships[0].label, "test_label")


if __name__ == '__main__':
    unittest.main()
