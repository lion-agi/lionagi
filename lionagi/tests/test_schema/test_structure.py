from lionagi.core.schema.structure import *
import unittest


class TestRelationship(unittest.TestCase):

    def setUp(self):
        self.relationship = Relationship(source_node_id="node1", target_node_id="node2")

    def test_add_condition(self):
        self.relationship.add_condition({"key": "value"})
        self.assertIn("key", self.relationship.condition)
        self.assertEqual(self.relationship.condition["key"], "value")

    def test_remove_condition_existing_key(self):
        self.relationship.add_condition({"key": "value"})
        removed_value = self.relationship.remove_condition("key")
        self.assertEqual(removed_value, "value")
        self.assertNotIn("key", self.relationship.condition)

    def test_remove_condition_non_existing_key(self):
        with self.assertRaises(KeyError):
            self.relationship.remove_condition("non_existing_key")

    def test_condition_exists_true(self):
        self.relationship.add_condition({"key": "value"})
        self.assertTrue(self.relationship.condition_exists("key"))

    def test_condition_exists_false(self):
        self.assertFalse(self.relationship.condition_exists("non_existing_key"))

    def test_get_condition_specific_key(self):
        self.relationship.add_condition({"key": "value"})
        condition_value = self.relationship.get_condition("key")
        self.assertEqual(condition_value, "value")

    def test_get_condition_all(self):
        self.relationship.add_condition({"key": "value"})
        conditions = self.relationship.get_condition()
        self.assertEqual(conditions, {"key": "value"})

    def test_get_condition_non_existing_key(self):
        with self.assertRaises(ValueError):
            self.relationship.get_condition("non_existing_key")


class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
        self.node1 = BaseNode(id_='node1')
        self.node2 = BaseNode(id_='node2')
        self.relationship = Relationship(id_='rel1', source_node_id='node1',
                                         target_node_id='node2')

    def test_add_node(self):
        self.graph.add_node(self.node1)
        self.assertIn('node1', self.graph.nodes)

    def test_add_relationship(self):
        self.graph.add_node(self.node1)
        self.graph.add_node(self.node2)
        self.graph.add_relationship(self.relationship)
        self.assertIn('rel1', self.graph.relationships)


class TestStructure(unittest.TestCase):

    def setUp(self):
        self.structure = Structure()
        self.node1 = BaseNode(id_='node1')
        self.node2 = BaseNode(id_='node2')
        self.relationship = Relationship(id_='rel1', source_node_id='node1',
                                         target_node_id='node2')

    def test_add_node(self):
        self.structure.add_node(self.node1)
        self.assertIn('node1', self.structure.graph.nodes)

    def test_add_relationship(self):
        self.structure.add_node(self.node1)
        self.structure.add_node(self.node2)
        self.structure.add_relationship(self.relationship)
        self.assertIn('rel1', self.structure.graph.relationships)


if __name__ == '__main__':
    unittest.main()
