import unittest
from unittest.mock import MagicMock
from lionagi.core.schema.edge import Edge, SourceType, Condition

class TestSourceType(unittest.TestCase):
    def test_source_type_values(self):
        self.assertEqual(SourceType.STRUCTURE, "structure")
        self.assertEqual(SourceType.EXECUTABLE, "executable")

class ConcreteCondition(Condition):
    def __call__(self, source_obj):
        return True

class TestCondition(unittest.TestCase):
    def test_init_with_source_type_enum(self):
        condition = ConcreteCondition(SourceType.STRUCTURE)
        self.assertEqual(condition.source_type, SourceType.STRUCTURE)

    def test_init_with_source_type_str(self):
        condition = ConcreteCondition("executable")
        self.assertEqual(condition.source_type, SourceType.EXECUTABLE)

    def test_init_with_invalid_source_type(self):
        with self.assertRaises(ValueError):
            ConcreteCondition("invalid_type")

    def test_call_implemented(self):
        condition = ConcreteCondition(SourceType.STRUCTURE)
        self.assertTrue(condition(None))

class TestEdge(unittest.TestCase):
    def setUp(self):
        self.edge = Edge(source_node_id="node1", target_node_id="node2")

    def test_init(self):
        self.assertEqual(self.edge.source_node_id, "node1")
        self.assertEqual(self.edge.target_node_id, "node2")
        self.assertFalse(self.edge.bundle)
        self.assertIsNone(self.edge.condition)

    def test_add_condition(self):
        condition = MagicMock(spec=Condition)
        self.edge.add_condition(condition)
        self.assertEqual(self.edge.condition, condition)

    def test_add_invalid_condition(self):
        with self.assertRaises(ValueError):
            self.edge.add_condition("invalid_condition")

    def test_check_condition(self):
        condition = MagicMock(spec=Condition)
        condition.return_value = True
        self.edge.condition = condition
        source_obj = MagicMock()
        self.assertTrue(self.edge.check_condition(source_obj))
        condition.assert_called_once_with(source_obj)

    def test_check_invalid_condition(self):
        self.edge.condition = lambda x: 1 / 0
        with self.assertRaises(ValueError):
            self.edge.check_condition(None)

    def test_source_existed(self):
        obj = {"node1": {}}
        self.assertTrue(self.edge._source_existed(obj))

    def test_source_not_existed(self):
        obj = {"node3": {}}
        self.assertFalse(self.edge._source_existed(obj))

    def test_target_existed(self):
        obj = {"node2": {}}
        self.assertTrue(self.edge._target_existed(obj))

    def test_target_not_existed(self):
        obj = {"node3": {}}
        self.assertFalse(self.edge._target_existed(obj))

    def test_is_in(self):
        obj = {"node1": {}, "node2": {}}
        self.assertTrue(self.edge._is_in(obj))

    def test_is_in_missing_target(self):
        obj = {"node1": {}}
        with self.assertRaises(ValueError):
            self.edge._is_in(obj)

    def test_is_in_missing_source(self):
        obj = {"node2": {}}
        with self.assertRaises(ValueError):
            self.edge._is_in(obj)

    def test_str(self):
        self.edge.id_ = "edge_id"
        self.edge.label = "edge_label"
        expected_str = "Edge (id_=edge_id, from=node1, to=node2, label=edge_label)"
        self.assertEqual(str(self.edge), expected_str)

    def test_repr(self):
        self.edge.id_ = "edge_id"
        self.edge.content = "edge_content"
        self.edge.metadata = {"key": "value"}
        self.edge.label = "edge_label"
        expected_repr = (
            "Edge(id_=edge_id, from=node1, to=node2, "
            "content=edge_content, metadata={'key': 'value'}, label=edge_label)"
        )
        self.assertEqual(repr(self.edge), expected_repr)

if __name__ == "__main__":
    unittest.main()